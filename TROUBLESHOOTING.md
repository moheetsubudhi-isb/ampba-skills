# Troubleshooting

Find the message you saw, then follow the fix. If your problem is not here, run the installer's check, which reports what is installed where and what is missing:

```bash
bash install.sh --check
```

```powershell
.\install.ps1 -Check
```

## Installing

### "Bash blocked here (don't-ask mode)" or "Permission denied by permission mode"

Your assistant is running in a mode that refuses commands it has not been allowed to run. Nothing is wrong with the skills. Any one of these fixes it:

- Run the command yourself. In Claude Code, start the line with `!` so it runs in your shell: `! curl -fsSL https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.sh | bash`
- Switch to a mode that asks first: press Shift+Tab until the mode changes, or start with `claude --permission-mode default`.
- Allow the command once and for all: run `/permissions` and add `Bash(npx skills:*)` or `Bash(bash install.sh:*)`.
- Or run the install command in an ordinary terminal window.

### "npx: command not found" or npm errors

The `npx skills` route needs Node.js. Use the install script instead; it needs nothing but a shell:

```bash
curl -fsSL https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.sh | bash
```

### "Could not resolve host", "the download failed", timeouts

The machine cannot reach GitHub, often because of a VPN or company proxy.

- If you use a proxy, set it first: `export HTTPS_PROXY=http://proxy.example.com:8080`
- Or download the zip in a browser from https://github.com/moheetsubudhi-isb/business-analytics-skills/archive/refs/heads/main.zip, unzip it, and run `bash install.sh --source <unzipped folder>` (Windows: `.\install.ps1 -Source <unzipped folder>`).

### "cannot create" or "cannot write to" a skills folder

The folder belongs to another user, usually because something was once run with `sudo`.

- Fix the owner: `sudo chown -R "$(id -un)" ~/.claude ~/.agents`
- Or install into a folder you own that your assistant reads: `bash install.sh --target <folder>`

### "running scripts is disabled on this system" (Windows)

PowerShell's execution policy blocks downloaded script files. The one-line install (`irm ... | iex`) is not affected. For a downloaded `install.ps1`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### "a different '<name>' already exists there; skipped"

You already have a skill with that name that this installer did not put there. It was left alone on purpose. Rename yours, or replace it with `--force` (Windows: `-Force`).

### "<name> is linked to a local copy; left as it is"

That skill folder is a link to a copy of the repository, which is how contributors work. The installer never overwrites links. Update that copy with `git pull` instead.

### The old name `ampba-skills` still shows up

The marketplace was renamed. Remove the old one and add the new one:

```
/plugin marketplace remove ampba-skills
/plugin marketplace add moheetsubudhi-isb/business-analytics-skills
```

### A toolkit shows as version 0.1.0 with no licence

An older copy of the marketplace is cached. Run `/plugin marketplace update business-analytics-skills`, then reinstall the toolkit.

## Using

### A skill does not load by itself

- Restart the assistant or open a new chat; most tools read skills at start-up.
- Ask a real work question with some detail. Skills are written to stay quiet on bare definitions such as "what is a p-value?".
- Call it by name: `/skill-name` in Claude Code, Cursor and Copilot; `$skill-name` or `/skills` in Codex; `@skill-name` in ChatGPT.
- Check it is in a folder your tool reads:

| Tool | Personal folder | Project folder |
|---|---|---|
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Codex | `~/.agents/skills` | `.agents/skills` |
| Cursor | `~/.agents/skills`, `~/.cursor/skills`, `~/.claude/skills` | `.agents/skills`, `.cursor/skills`, `.claude/skills` |
| GitHub Copilot | `~/.agents/skills`, `~/.copilot/skills`, `~/.claude/skills` | `.agents/skills`, `.github/skills`, `.claude/skills` |
| Gemini CLI | `~/.agents/skills`, `~/.gemini/skills` | `.agents/skills`, `.gemini/skills` |

### A skill appears twice

Cursor and Copilot read both `~/.claude/skills` and `~/.agents/skills`. If both hold a copy, you see two. They are identical, so either works. To keep one, delete the copies in `~/.agents/skills` (Cursor and Copilot will still find `~/.claude/skills`), unless you also use Codex or Gemini CLI, which need `~/.agents/skills`.

### "needs numpy" (or pandas, scikit-learn) from a script

The scripts are optional checks. Install the packages with `python3 -m pip install --user numpy pandas scikit-learn`, or carry on without them: every skill does its check by hand on a small case when a script cannot run, and says so.

### Chat apps: no Skills option

- Claude (claude.ai and the desktop app): turn on code execution in Settings > Capabilities; on Team and Enterprise an owner enables Skills first.
- ChatGPT: skill upload depends on your plan. Without it, paste `dist/text/<skill>.md` into a Project's instructions.
- Microsoft 365 Copilot: skills are added to an agent in Agent Builder, which needs a Copilot licence.
- Gemini app: make a Gem and paste `dist/text/<skill>.md` into its instructions.

## Asking an assistant to install for you

Any assistant that can run commands can install the set. Paste this:

> Install the skills from https://github.com/moheetsubudhi-isb/business-analytics-skills. On macOS or Linux run `curl -fsSL https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.sh | bash -s -- --yes`; on Windows run `irm https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.ps1 | iex`. If you cannot run commands here, show me the command to run myself. Then tell me what the installer printed.
