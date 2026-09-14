#!/usr/bin/env python3
"""Build upload-ready copies of every skill into dist/.

  dist/<skill>.zip                 skill folder at the zip root: Claude, ChatGPT
  dist/microsoft-365/<skill>.zip   SKILL.md at the zip root: Microsoft 365 Copilot
  dist/text/<skill>.md             one file, references inlined: Gemini Gems, any chat

  python3 tools/build_bundles.py           rebuild dist/
  python3 tools/build_bundles.py --check   fail if dist/ is out of date (CI)

Zips are stored uncompressed with fixed timestamps so the same sources give the
same bytes on any machine, which is what lets CI check them.
"""
import io
import pathlib
import shutil
import sys
import zipfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
JUNK = {"__pycache__", ".DS_Store"}


def files(skill):
    return sorted(p for p in skill.rglob("*")
                  if p.is_file() and p.suffix != ".pyc"
                  and not JUNK & set(p.relative_to(skill).parts))


def zipped(skill, prefix):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for p in files(skill):
            info = zipfile.ZipInfo(prefix + p.relative_to(skill).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return buf.getvalue()


def flattened(skill):
    _, front, body = (skill / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
    parts = [f"# {skill.name}\n\nUse this skill when: {yaml.safe_load(front)['description']}\n",
             body.strip() + "\n"]
    for ref in sorted((skill / "references").glob("*.md")):
        parts.append(f"---\n\n## Reference: references/{ref.name}\n\n"
                     f"{ref.read_text(encoding='utf-8').strip()}\n")
    return "\n".join(parts).encode("utf-8")


def build():
    out = {}
    for skill in sorted(ROOT.glob("plugins/*/skills/*")):
        if (skill / "SKILL.md").exists():
            out[f"{skill.name}.zip"] = zipped(skill, skill.name + "/")
            out[f"microsoft-365/{skill.name}.zip"] = zipped(skill, "")
            out[f"text/{skill.name}.md"] = flattened(skill)
    return out


def main():
    want = build()
    if "--check" in sys.argv:
        have = {p.relative_to(DIST).as_posix(): p.read_bytes()
                for p in DIST.rglob("*") if p.is_file() and p.name not in JUNK}
        stale = sorted(k for k in want.keys() | have.keys() if want.get(k) != have.get(k))
        if stale:
            sys.exit("dist/ is out of date; run python3 tools/build_bundles.py\n  " + "\n  ".join(stale))
        print(f"dist/ up to date ({len(want)} files)")
        return
    shutil.rmtree(DIST, ignore_errors=True)
    for name, data in want.items():
        (DIST / name).parent.mkdir(parents=True, exist_ok=True)
        (DIST / name).write_bytes(data)
    print(f"wrote {len(want)} files to dist/")


if __name__ == "__main__":
    main()
