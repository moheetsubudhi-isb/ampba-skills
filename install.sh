#!/usr/bin/env bash
# Install Business Analytics Skills into every AI assistant found on this machine.
#
#   curl -fsSL https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.sh | bash
#   bash install.sh [options]
#
# Options
#   -y, --yes          install without asking (also used when no terminal is attached)
#   --dry-run          show what would happen and change nothing
#   --project          install into the current folder's project skill folders
#   --target DIR       install into DIR instead of the detected folders (repeatable)
#   --only LIST        comma-separated toolkits or skills, e.g. statistics-toolkit,ml-data-audit
#   --force            replace a folder with the same name even if this installer did not create it
#   --check            report what is installed where, and whether the scripts' Python packages are present
#   --uninstall        remove only the skills this installer put in place
#   --source DIR       use a local copy of the repository instead of downloading
#   --ref REF          branch or tag to download (default: main)
#   -h, --help         show this help
#
# Where skills go: Claude Code reads ~/.claude/skills. Codex, Cursor, GitHub Copilot and
# Gemini CLI all read ~/.agents/skills, and Cursor and Copilot also read ~/.claude/skills.
# The installer picks the smallest set of folders that covers every tool it finds.

set -u

REPO="moheetsubudhi-isb/business-analytics-skills"
REF="main"
MANIFEST=".business-analytics-skills"
YES=0 DRY=0 PROJECT=0 FORCE=0 MODE=install SOURCE="" ONLY=""
TARGETS=()

say()  { printf '%s\n' "$*"; }
step() { printf '\n==> %s\n' "$*"; }
warn() { printf '  ! %s\n' "$*"; }
die() {
    printf '\nInstall stopped: %s\n\nWhat to do:\n' "$1"
    shift
    for line in "$@"; do printf '  - %s\n' "$line"; done
    printf '\nMore fixes: https://github.com/%s/blob/main/TROUBLESHOOTING.md\n' "$REPO"
    exit 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        -y|--yes) YES=1 ;;
        --dry-run) DRY=1 ;;
        --project) PROJECT=1 ;;
        --force) FORCE=1 ;;
        --check) MODE=check ;;
        --uninstall) MODE=uninstall ;;
        --target) [ $# -ge 2 ] || die "--target needs a folder" "Example: bash install.sh --target ~/my-agent/skills"; TARGETS+=("$2"); shift ;;
        --only) [ $# -ge 2 ] || die "--only needs a list" "Example: bash install.sh --only statistics-toolkit"; ONLY="$2"; shift ;;
        --source) [ $# -ge 2 ] || die "--source needs a folder" "Example: bash install.sh --source ./business-analytics-skills"; SOURCE="$2"; shift ;;
        --ref) [ $# -ge 2 ] || die "--ref needs a branch or tag" "Example: bash install.sh --ref main"; REF="$2"; shift ;;
        -h|--help) sed -n '2,23p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//' | grep . || say "Options: --yes --dry-run --project --target DIR --only LIST --force --check --uninstall --source DIR --ref REF"; exit 0 ;;
        *) die "unknown option '$1'" "See the options: bash install.sh --help, or https://github.com/$REPO#install-in-terminal-and-ide-tools" ;;
    esac
    shift
done

has() { command -v "$1" >/dev/null 2>&1; }
# how to run this installer again, matching how it was started this time
if [ -f "${BASH_SOURCE[0]:-}" ]; then
    RERUN="bash $(basename "${BASH_SOURCE[0]}")"
else
    RERUN="curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | bash -s --"
fi
base() { if [ "$PROJECT" = 1 ]; then printf '%s' "$PWD"; else printf '%s' "$HOME"; fi; }

# ---------------------------------------------------------------- detect tools
detect() {
    FOUND=()
    { [ -d "$HOME/.claude" ] || has claude; } && FOUND+=("Claude Code")
    { [ -d "$HOME/.codex" ] || has codex; } && FOUND+=("Codex")
    { [ -d "$HOME/.cursor" ] || has cursor; } && FOUND+=("Cursor")
    { [ -d "$HOME/.copilot" ] || has copilot || [ -d "$HOME/.vscode" ] || has code; } && FOUND+=("GitHub Copilot / VS Code")
    { [ -d "$HOME/.gemini" ] || has gemini; } && FOUND+=("Gemini CLI")
}
found() { local t; for t in "${FOUND[@]+"${FOUND[@]}"}"; do [ "$t" = "$1" ] && return 0; done; return 1; }

choose_targets() {
    [ ${#TARGETS[@]} -gt 0 ] && return
    local b; b="$(base)"
    found "Claude Code" && TARGETS+=("$b/.claude/skills")
    # Codex and Gemini read only ~/.agents/skills; without Claude Code it is also the
    # folder Cursor and Copilot share, so it is the universal default.
    if found "Codex" || found "Gemini CLI" || ! found "Claude Code"; then
        TARGETS+=("$b/.agents/skills")
    fi
}

# ---------------------------------------------------------------- get the files
fetch_source() {
    if [ -n "$SOURCE" ]; then
        [ -d "$SOURCE/plugins" ] || die "'$SOURCE' is not a copy of the repository (no plugins/ folder)" \
            "Point --source at the folder that contains plugins/, README.md and install.sh"
        return
    fi
    local here; here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)"
    if [ -n "$here" ] && [ -d "$here/plugins" ] && [ -f "$here/install.sh" ]; then SOURCE="$here"; return; fi

    TMP="$(mktemp -d 2>/dev/null || mktemp -d -t bas)" || die "could not create a temporary folder" "Free some disk space, or set TMPDIR to a writable folder and run again"
    trap 'rm -rf "$TMP"' EXIT
    local url="https://codeload.github.com/$REPO/tar.gz/$REF"
    step "Downloading $REPO ($REF)"
    if has curl; then
        curl -fsSL "$url" -o "$TMP/src.tgz" || die "the download failed" \
            "Check the internet connection, VPN or company proxy (set HTTPS_PROXY if you use one)" \
            "Or download https://github.com/$REPO/archive/refs/heads/$REF.zip in a browser, unzip it, and run: bash install.sh --source <unzipped folder>"
    elif has wget; then
        wget -q "$url" -O "$TMP/src.tgz" || die "the download failed" \
            "Check the internet connection, VPN or company proxy" \
            "Or download https://github.com/$REPO/archive/refs/heads/$REF.zip in a browser, unzip it, and run: bash install.sh --source <unzipped folder>"
    else
        die "neither curl nor wget is available" \
            "Install curl, or download https://github.com/$REPO/archive/refs/heads/$REF.zip in a browser, unzip it, and run: bash install.sh --source <unzipped folder>"
    fi
    has tar || die "tar is not available" "Unzip the download by hand and run: bash install.sh --source <unzipped folder>"
    tar -xzf "$TMP/src.tgz" -C "$TMP" || die "the download could not be unpacked" "Run the command again; if it repeats, use the browser download described above"
    SOURCE="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
    [ -d "$SOURCE/plugins" ] || die "the download did not contain the skills" "Check that '$REF' is a real branch or tag of $REPO"
}

list_skills() {
    SKILLS=()
    local d name toolkit
    for d in "$SOURCE"/plugins/*/skills/*/; do
        [ -f "$d/SKILL.md" ] || continue
        name="$(basename "$d")"
        toolkit="$(basename "$(dirname "$(dirname "$d")")")"
        if [ -n "$ONLY" ]; then
            case ",$ONLY," in *",$name,"*|*",$toolkit,"*) ;; *) continue ;; esac
        fi
        SKILLS+=("${d%/}")
    done
    [ ${#SKILLS[@]} -gt 0 ] || die "no skills matched '$ONLY'" "Use toolkit names (statistics-toolkit) or skill names (ml-data-audit), separated by commas"
}

owned() { [ -f "$1/$MANIFEST" ] && grep -qx "$2" "$1/$MANIFEST"; }

# ---------------------------------------------------------------- modes
python_check() {
    local py=""
    for c in python3 python; do has "$c" && { py="$c"; break; }; done
    if [ -z "$py" ]; then
        say "  Python: not found. The skills still work; their checks run by hand instead of by script."
        say "  To enable the scripts, install Python 3 from https://www.python.org/downloads/ and run:"
        say "    python3 -m pip install --user numpy pandas scikit-learn"
        return
    fi
    local missing
    missing="$("$py" - <<'EOF' 2>/dev/null
import importlib.util
print(" ".join(m for m in ("numpy", "pandas", "sklearn") if importlib.util.find_spec(m) is None))
EOF
)"
    if [ -z "$missing" ]; then
        say "  Python: $("$py" --version 2>&1) with numpy, pandas and scikit-learn. Every script can run."
    else
        say "  Python: $("$py" --version 2>&1), missing: ${missing/sklearn/scikit-learn}."
        say "  The skills still work; scripts that need these fall back to checks by hand. To enable them:"
        say "    $py -m pip install --user ${missing/sklearn/scikit-learn}"
    fi
}

do_check() {
    step "Installed skills"
    local b any=0 dir n
    for b in "$HOME" "$PWD"; do
        for dir in "$b/.claude/skills" "$b/.agents/skills" "$b/.cursor/skills" "$b/.copilot/skills" "$b/.gemini/skills" "$b/.github/skills"; do
            [ -f "$dir/$MANIFEST" ] || continue
            n="$(grep -vc '^#' "$dir/$MANIFEST")"
            say "  $dir: $n skills ($(grep '^# ' "$dir/$MANIFEST" | head -n 1 | sed 's/^# //'))"
            any=1
        done
    done
    [ "$any" = 1 ] || say "  None installed by this installer yet. Run: $RERUN"
    step "Python for the scripts"
    python_check
}

do_uninstall() {
    local b dir name removed=0
    for b in "$HOME" "$PWD"; do
        for dir in "$b/.claude/skills" "$b/.agents/skills" "$b/.cursor/skills" "$b/.copilot/skills" "$b/.gemini/skills" "$b/.github/skills" "${TARGETS[@]+"${TARGETS[@]}"}"; do
            [ -f "$dir/$MANIFEST" ] || continue
            step "Removing from $dir"
            while IFS= read -r name; do
                case "$name" in ''|'#'*) continue ;; esac
                if [ -L "$dir/$name" ]; then warn "$name is a link to a local copy; left in place"; continue; fi
                [ "$DRY" = 1 ] && { say "  would remove $name"; continue; }
                rm -rf "${dir:?}/$name" && removed=$((removed + 1))
            done < "$dir/$MANIFEST"
            [ "$DRY" = 1 ] || rm -f "$dir/$MANIFEST"
        done
    done
    say ""
    say "Removed $removed skill folders. Skills you added yourself were not touched."
}

do_install() {
    detect
    choose_targets
    fetch_source
    list_skills

    step "Plan"
    if [ ${#FOUND[@]} -gt 0 ]; then
        say "  Assistants found: $(IFS=,; printf '%s' "${FOUND[*]}" | sed 's/,/, /g')"
    else
        say "  No assistant found yet. Installing into ~/.agents/skills, the shared folder that Codex,"
        say "  Cursor, GitHub Copilot and Gemini CLI read. Claude Code users: rerun after installing Claude Code."
    fi
    say "  Skills: ${#SKILLS[@]}"
    local t
    for t in "${TARGETS[@]}"; do say "  Into: $t"; done
    [ "$DRY" = 1 ] && { say ""; say "Dry run: nothing was changed."; return; }

    if [ "$YES" = 0 ] && [ -r /dev/tty ] && [ -w /dev/tty ]; then
        printf '\nInstall now? [Y/n] ' > /dev/tty
        local answer=""
        read -r answer < /dev/tty || answer=""
        case "$answer" in [Nn]*) say "Nothing installed."; exit 0 ;; esac
    fi

    local installed=0 skipped=0 linked=0 src name dest stamp
    stamp="# $REPO@$REF installed $(date '+%Y-%m-%d %H:%M')"
    for t in "${TARGETS[@]}"; do
        step "Installing into $t"
        mkdir -p "$t" 2>/dev/null || die "cannot create $t" \
            "Check that you own the folder above it: ls -ld \"$(dirname "$t")\"" \
            "Or install somewhere you can write: bash install.sh --target <folder your assistant reads>"
        [ -w "$t" ] || die "cannot write to $t" \
            "Fix the folder's owner: sudo chown -R \"$(id -un)\" \"$t\"" \
            "Or install somewhere you can write: bash install.sh --target <folder your assistant reads>"
        local kept=()
        linked=0
        if [ -f "$t/$MANIFEST" ]; then
            while IFS= read -r name; do case "$name" in ''|'#'*) ;; *) kept+=("$name") ;; esac; done < "$t/$MANIFEST"
        fi
        for src in "${SKILLS[@]}"; do
            name="$(basename "$src")"
            dest="$t/$name"
            if [ -L "$dest" ]; then
                linked=$((linked + 1)); continue
            fi
            if [ -e "$dest" ] && ! owned "$t" "$name" && [ "$FORCE" = 0 ]; then
                warn "a different '$name' already exists there; skipped (use --force to replace it)"
                skipped=$((skipped + 1)); continue
            fi
            rm -rf "${dest:?}"
            cp -R "$src" "$dest" || die "copying $name failed" "Check free disk space and permissions on $t"
            kept+=("$name")
            installed=$((installed + 1))
        done
        { say "$stamp"; printf '%s\n' "${kept[@]+"${kept[@]}"}" | sort -u; } > "$t/$MANIFEST"
        local ok=0
        for src in "${SKILLS[@]}"; do
            [ -f "$t/$(basename "$src")/SKILL.md" ] && ok=$((ok + 1))
        done
        [ "$linked" -gt 0 ] && say "  $linked of them are links to a local copy of this repository (yours, left as they are; update with git pull)"
        say "  Verified: $ok of ${#SKILLS[@]} skills are in place in $t"
        say "  Check one: $t/$(basename "${SKILLS[0]}")/SKILL.md"
    done

    step "Python for the scripts"
    python_check

    step "Done: ${#SKILLS[@]} skills into ${#TARGETS[@]} folder(s), $skipped skipped"
    say "Restart your assistant (or open a new chat), then ask a normal work question. Skills load by"
    say "themselves when a question matches. To call one directly:"
    found "Claude Code" && say "  Claude Code      type / and the skill name"
    found "Codex" && say "  Codex            type \$ and the skill name, or run /skills"
    found "Cursor" && say "  Cursor           type / in Agent chat and search for the skill"
    found "GitHub Copilot / VS Code" && say "  Copilot          type /skills in Copilot Chat"
    found "Gemini CLI" && say "  Gemini CLI       run: gemini skills list --all"
    [ ${#FOUND[@]} -eq 0 ] && say "  Any assistant    ask it to use the skill by name"
    say ""
    say "Chat apps (claude.ai, ChatGPT, Microsoft 365 Copilot, Gemini) need an upload instead:"
    say "  https://github.com/$REPO#use-in-chat-tools"
    say "Update later by running this command again. Remove with: $RERUN --uninstall"
}

case "$MODE" in
    check) do_check ;;
    uninstall) do_uninstall ;;
    install) do_install ;;
esac
