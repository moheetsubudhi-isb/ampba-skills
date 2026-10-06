# Install Business Analytics Skills into every AI assistant found on this Windows machine.
#
#   irm https://raw.githubusercontent.com/moheetsubudhi-isb/business-analytics-skills/main/install.ps1 | iex
#   .\install.ps1 [-Yes] [-DryRun] [-Project] [-Target DIR] [-Only LIST] [-Force] [-Check] [-Uninstall] [-Source DIR] [-Ref REF]
#
# Works in Windows PowerShell 5.1 and PowerShell 7. Same behaviour as install.sh:
# Claude Code reads ~\.claude\skills; Codex, Cursor, GitHub Copilot and Gemini CLI read
# ~\.agents\skills; Cursor and Copilot also read ~\.claude\skills.
param(
    [switch]$Yes,
    [switch]$DryRun,
    [switch]$Project,
    [string[]]$Target = @(),
    [string]$Only = "",
    [switch]$Force,
    [switch]$Check,
    [switch]$Uninstall,
    [string]$Source = "",
    [string]$Ref = "main",
    [string]$HomeDir = $HOME
)

$ErrorActionPreference = "Stop"
$Repo = "moheetsubudhi-isb/business-analytics-skills"
$Manifest = ".business-analytics-skills"
# how to run this installer again with options, matching how it was started this time
if ($PSCommandPath) { $Rerun = ".\install.ps1" }
else { $Rerun = "& ([scriptblock]::Create((irm https://raw.githubusercontent.com/$Repo/main/install.ps1)))" }

function Say([string]$m) { Write-Host $m }
function Step([string]$m) { Write-Host ""; Write-Host "==> $m" }
function Warn([string]$m) { Write-Host "  ! $m" -ForegroundColor Yellow }
function Stop-Install([string]$why, [string[]]$todo) {
    Write-Host ""
    Write-Host "Install stopped: $why" -ForegroundColor Red
    Write-Host ""
    Write-Host "What to do:"
    foreach ($t in $todo) { Write-Host "  - $t" }
    Write-Host ""
    Write-Host "More fixes: https://github.com/$Repo/blob/main/TROUBLESHOOTING.md"
    throw "install stopped"
}
function Has([string]$cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Get-Tools {
    $found = @()
    if ((Test-Path "$HomeDir\.claude") -or (Has "claude")) { $found += "Claude Code" }
    if ((Test-Path "$HomeDir\.codex") -or (Has "codex")) { $found += "Codex" }
    if ((Test-Path "$HomeDir\.cursor") -or (Has "cursor")) { $found += "Cursor" }
    if ((Test-Path "$HomeDir\.copilot") -or (Has "copilot") -or (Test-Path "$HomeDir\.vscode") -or (Has "code")) { $found += "GitHub Copilot / VS Code" }
    if ((Test-Path "$HomeDir\.gemini") -or (Has "gemini")) { $found += "Gemini CLI" }
    return $found
}

function Get-Targets([string[]]$found) {
    if ($Target.Count -gt 0) { return $Target }
    $base = if ($Project) { (Get-Location).Path } else { $HomeDir }
    $t = @()
    if ($found -contains "Claude Code") { $t += (Join-Path $base ".claude\skills") }
    if (($found -contains "Codex") -or ($found -contains "Gemini CLI") -or -not ($found -contains "Claude Code")) {
        $t += (Join-Path $base ".agents\skills")
    }
    return $t
}

function Get-SourceFolder {
    if ($Source) {
        if (-not (Test-Path (Join-Path $Source "plugins"))) {
            Stop-Install "'$Source' is not a copy of the repository (no plugins folder)" @("Point -Source at the folder that contains plugins, README.md and install.ps1")
        }
        return (Resolve-Path $Source).Path
    }
    if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "plugins"))) { return $PSScriptRoot }

    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("bas-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $zip = Join-Path $tmp "src.zip"
    Step "Downloading $Repo ($Ref)"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/$Repo/zip/$Ref" -OutFile $zip
    } catch {
        Stop-Install "the download failed ($($_.Exception.Message))" @(
            "Check the internet connection, VPN or company proxy",
            "Or download https://github.com/$Repo/archive/refs/heads/$Ref.zip in a browser, unzip it, and run: .\install.ps1 -Source <unzipped folder>")
    }
    try { Expand-Archive -Path $zip -DestinationPath $tmp -Force } catch {
        Stop-Install "the download could not be unpacked" @("Unzip it by hand and run: .\install.ps1 -Source <unzipped folder>")
    }
    $dir = Get-ChildItem -Path $tmp -Directory | Select-Object -First 1
    if (-not $dir -or -not (Test-Path (Join-Path $dir.FullName "plugins"))) {
        Stop-Install "the download did not contain the skills" @("Check that '$Ref' is a real branch or tag of $Repo")
    }
    return $dir.FullName
}

function Get-Skills([string]$src) {
    $wanted = @()
    if ($Only) { $wanted = $Only.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ } }
    $skills = @()
    foreach ($tk in Get-ChildItem -Path (Join-Path $src "plugins") -Directory) {
        $sk = Join-Path $tk.FullName "skills"
        if (-not (Test-Path $sk)) { continue }
        foreach ($d in Get-ChildItem -Path $sk -Directory) {
            if (-not (Test-Path (Join-Path $d.FullName "SKILL.md"))) { continue }
            if ($wanted.Count -gt 0 -and -not (($wanted -contains $d.Name) -or ($wanted -contains $tk.Name))) { continue }
            $skills += $d
        }
    }
    if ($skills.Count -eq 0) {
        Stop-Install "no skills matched '$Only'" @("Use toolkit names (statistics-toolkit) or skill names (ml-data-audit), separated by commas")
    }
    return $skills
}

function Read-Manifest([string]$dir) {
    $f = Join-Path $dir $Manifest
    if (-not (Test-Path $f)) { return }
    return @(Get-Content $f | Where-Object { $_ -and -not $_.StartsWith("#") })
}

function Test-Python {
    $py = $null
    foreach ($c in @("python", "py", "python3")) { if (Has $c) { $py = $c; break } }
    if (-not $py) {
        Say "  Python: not found. The skills still work; their checks run by hand instead of by script."
        Say "  To enable the scripts, install Python 3 from https://www.python.org/downloads/ and run:"
        Say "    python -m pip install --user numpy pandas scikit-learn"
        return
    }
    $code = "import importlib.util; print(' '.join(m for m in ('numpy','pandas','sklearn') if importlib.util.find_spec(m) is None))"
    try { $missing = (& $py -c $code 2>$null) -join "" } catch { $missing = "numpy pandas sklearn" }
    $missing = $missing.Trim() -replace "sklearn", "scikit-learn"
    $ver = (& $py --version 2>&1) -join ""
    if (-not $missing) { Say "  Python: $ver with numpy, pandas and scikit-learn. Every script can run." }
    else {
        Say "  Python: $ver, missing: $missing."
        Say "  The skills still work; scripts that need these fall back to checks by hand. To enable them:"
        Say "    $py -m pip install --user $missing"
    }
}

function Get-KnownDirs {
    $dirs = @()
    foreach ($b in @($HomeDir, (Get-Location).Path)) {
        foreach ($s in @(".claude\skills", ".agents\skills", ".cursor\skills", ".copilot\skills", ".gemini\skills", ".github\skills")) {
            $dirs += (Join-Path $b $s)
        }
    }
    return ($dirs + $Target)
}

function Invoke-Check {
    Step "Installed skills"
    $any = $false
    foreach ($d in @(Get-KnownDirs)) {
        $f = Join-Path $d $Manifest
        if (-not (Test-Path $f)) { continue }
        $names = @(Read-Manifest $d)
        $stamp = (Get-Content $f | Where-Object { $_.StartsWith("# ") } | Select-Object -First 1)
        Say "  ${d}: $($names.Count) skills ($($stamp -replace '^# ', ''))"
        $any = $true
    }
    if (-not $any) { Say "  None installed by this installer yet. Run: $Rerun" }
    Step "Python for the scripts"
    Test-Python
}

function Invoke-Uninstall {
    $removed = 0
    foreach ($d in @(Get-KnownDirs)) {
        $f = Join-Path $d $Manifest
        if (-not (Test-Path $f)) { continue }
        Step "Removing from $d"
        foreach ($n in @(Read-Manifest $d)) {
            $p = Join-Path $d $n
            $item = Get-Item $p -ErrorAction SilentlyContinue
            if ($item -and $item.LinkType) { Warn "$n is a link to a local copy; left in place"; continue }
            if ($DryRun) { Say "  would remove $n"; continue }
            if ($item) { Remove-Item -Recurse -Force $p; $removed++ }
        }
        if (-not $DryRun) { Remove-Item -Force $f }
    }
    Say ""
    Say "Removed $removed skill folders. Skills you added yourself were not touched."
}

function Invoke-Install {
    $found = @(Get-Tools)
    $targets = @(Get-Targets $found)
    $src = Get-SourceFolder
    $skills = @(Get-Skills $src)

    Step "Plan"
    if ($found.Count -gt 0) { Say "  Assistants found: $($found -join ', ')" }
    else {
        Say "  No assistant found yet. Installing into ~\.agents\skills, the shared folder that Codex,"
        Say "  Cursor, GitHub Copilot and Gemini CLI read. Claude Code users: rerun after installing Claude Code."
    }
    Say "  Skills: $($skills.Count)"
    foreach ($t in $targets) { Say "  Into: $t" }
    if ($DryRun) { Say ""; Say "Dry run: nothing was changed."; return }

    $interactive = [Environment]::UserInteractive -and -not $Yes -and -not [Console]::IsInputRedirected
    if ($interactive) {
        $answer = Read-Host "`nInstall now? [Y/n]"
        if ($answer -match "^[Nn]") { Say "Nothing installed."; return }
    }

    $skipped = 0
    $stamp = "# $Repo@$Ref installed $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    foreach ($t in $targets) {
        Step "Installing into $t"
        try { New-Item -ItemType Directory -Force -Path $t | Out-Null } catch {
            Stop-Install "cannot create $t" @("Check that you can write to $(Split-Path $t -Parent)", "Or install somewhere you can write: .\install.ps1 -Target <folder your assistant reads>")
        }
        $kept = [System.Collections.Generic.List[string]]::new()
        foreach ($n in @(Read-Manifest $t)) { $kept.Add($n) }
        foreach ($s in $skills) {
            $dest = Join-Path $t $s.Name
            $item = Get-Item $dest -ErrorAction SilentlyContinue
            if ($item -and $item.LinkType) { Warn "$($s.Name) is linked to a local copy; left as it is"; $skipped++; continue }
            if ($item -and -not ($kept -contains $s.Name) -and -not $Force) {
                Warn "a different '$($s.Name)' already exists there; skipped (use -Force to replace it)"; $skipped++; continue
            }
            try {
                if ($item) { Remove-Item -Recurse -Force $dest }
                Copy-Item -Recurse -Force -Path $s.FullName -Destination $dest
            } catch {
                Stop-Install "copying $($s.Name) failed ($($_.Exception.Message))" @("Check free disk space and permissions on $t")
            }
            if (-not ($kept -contains $s.Name)) { $kept.Add($s.Name) }
        }
        $lines = @($stamp) + ($kept | Sort-Object -Unique)
        Set-Content -Path (Join-Path $t $Manifest) -Value $lines -Encoding UTF8
        $ok = @($kept | Where-Object { Test-Path (Join-Path (Join-Path $t $_) "SKILL.md") }).Count
        Say "  Verified: $ok skills from this set are in $t"
        Say "  Check one: $(Join-Path (Join-Path $t $skills[0].Name) 'SKILL.md')"
    }

    Step "Python for the scripts"
    Test-Python

    Step "Done: $($skills.Count) skills into $($targets.Count) folder(s), $skipped skipped"
    Say "Restart your assistant (or open a new chat), then ask a normal work question. Skills load by"
    Say "themselves when a question matches. To call one directly:"
    if ($found -contains "Claude Code") { Say "  Claude Code      type / and the skill name" }
    if ($found -contains "Codex") { Say "  Codex            type `$ and the skill name, or run /skills" }
    if ($found -contains "Cursor") { Say "  Cursor           type / in Agent chat and search for the skill" }
    if ($found -contains "GitHub Copilot / VS Code") { Say "  Copilot          type /skills in Copilot Chat" }
    if ($found -contains "Gemini CLI") { Say "  Gemini CLI       run: gemini skills list --all" }
    if ($found.Count -eq 0) { Say "  Any assistant    ask it to use the skill by name" }
    Say ""
    Say "Chat apps (claude.ai, ChatGPT, Microsoft 365 Copilot, Gemini) need an upload instead:"
    Say "  https://github.com/$Repo#use-in-chat-tools"
    Say "Update later by running this command again. Remove with: $Rerun -Uninstall"
}

try {
    if ($Check) { Invoke-Check }
    elseif ($Uninstall) { Invoke-Uninstall }
    else { Invoke-Install }
} catch {
    if ($_.Exception.Message -ne "install stopped") {
        Write-Host ""
        Write-Host "Install stopped: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "More fixes: https://github.com/$Repo/blob/main/TROUBLESHOOTING.md"
    }
    # exit only when run as a file; under "irm | iex" an exit would close the user's window
    if ($PSCommandPath) { exit 1 }
}
