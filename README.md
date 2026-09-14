# AMPBA Skills

Skills that make an AI assistant work like a decision scientist and an advisor, not just a calculator. Each skill:

- asks what the work is for, but only when the answer would change the result;
- follows a real method, step by step;
- runs a check wherever there is logic to verify;
- hands back a plain-language decision brief for the decision owner, plus a technical appendix for the people who build it.

The methods come from analytics coursework at ISB (AMPBA), rewritten from scratch for everyday work. The repository contains no course slides, cases, datasets or faculty material, and every example is invented.

## Skills

12 skills in two toolkits. Each one loads on its own when a request matches it, so nobody has to name it.

**Optimisation toolkit** (`optimization-toolkit`)

| Skill | Use it when |
|---|---|
| `optimization-formulation` | You need to turn a business decision into a model and a recommendation, or judge whether extra capacity is worth paying for |
| `logical-constraints` | You need yes/no business rules ("if we open A, we must also open B") written as correct constraints, with proof |
| `shortage-allocation-fairness` | Supply falls short of demand and you have to choose, and price, a definition of fair |
| `exact-vs-heuristic` | A solver is too slow for the real problem size and you need to set expectations on speed and quality |
| `or-model-test-plan` | You need to decide whether a model's plans can be trusted before go-live |

**ML toolkit** (`ml-toolkit`)

| Skill | Use it when |
|---|---|
| `ml-problem-framing` | You are deciding whether ML should solve a problem at all, and what the target, labels, baseline and metric should be |
| `ml-data-audit` | You are deciding whether a dataset can support a model: leakage, label quality, missing values, train/serve differences |
| `feature-engineering` | You are designing or debugging features and need them to be correct at the moment of prediction |
| `dimensionality-reduction` | There are too many features: choosing between PCA, Fisher/LDA, feature selection and 2-D pictures |
| `clustering-and-segmentation` | You are segmenting customers or records and need to choose k-means, hierarchical, DBSCAN, GMM or a mixed-type method |
| `model-selection-and-validation` | You are choosing a model and a validation split that proves it generalises |
| `classification-metrics-and-threshold` | You are judging a classifier by what its errors cost, and setting the decision threshold |

See [catalog.md](catalog.md) for the course modules behind each skill and its trigger-test score.

## Where the skills work

Every skill is one folder with a `SKILL.md` file, in the open [Agent Skills](https://agentskills.io) format. The same folder works in each tool below without changes.

| Where | Kind | Loads the skill by itself | Runs the scripts | How to install |
|---|---|---|---|---|
| Claude Code | Terminal / IDE | Yes | Yes | [Plugin or folder](#claude-code) |
| Codex (CLI, IDE, ChatGPT desktop app) | Terminal / IDE | Yes | Yes | [Folder](#codex-and-the-chatgpt-desktop-app) |
| Cursor | IDE | Yes | Yes | [Folder](#cursor) |
| GitHub Copilot (VS Code, Copilot CLI) | IDE / terminal | Yes | Yes | [Folder](#github-copilot-in-vs-code-and-copilot-cli) |
| Gemini CLI | Terminal | Yes | Yes | [Folder](#gemini-cli) |
| Other agents (OpenCode, Cline and more) | Terminal / IDE | Yes | Yes | [One command](#one-command-for-every-terminal-tool) |
| Claude (claude.ai and the desktop app) | Chat | Usually; name the skill if it doesn't | Yes, with code execution on | [Upload a zip](#claude-chat) |
| ChatGPT | Chat | Yes | Yes | [Upload a zip](#chatgpt) |
| Microsoft 365 Copilot | Chat | Yes | Yes, in a sandbox; ML scripts need their packages preinstalled | [Upload a zip to an agent](#microsoft-365-copilot) |
| Gemini app | Chat | No, lives inside a Gem | No | [Make a Gem](#gemini-app-gems) |
| Microsoft Copilot app, or any other chat | Chat | No | No | [Paste the text](#any-other-chat) |

Where code cannot run, each skill still guides the method and tells the assistant to do its checks by hand on a small case.

## Install in terminal and IDE tools

Start by downloading the repository. While it is private, only people added as collaborators can clone it.

```bash
git clone https://github.com/moheetsubudhi-isb/ampba-skills.git
```

The scripts need Python 3. The ML scripts also need `numpy`, `pandas` and `scikit-learn`:

```bash
pip install -r ampba-skills/requirements.txt
```

**Personal or project install.** Each tool below reads skills from a folder in your home directory, which makes them available in every project, and from a folder inside a project, which shares them with everyone who clones that project. Copy the skill folders into whichever one you want.

### One command for every terminal tool

The open-source [`skills` CLI](https://github.com/vercel-labs/skills) installs into Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and many other agents at once. It uses your existing GitHub login, so it works with this private repository.

```bash
npx skills add moheetsubudhi-isb/ampba-skills --list
```

```bash
npx skills add moheetsubudhi-isb/ampba-skills -g -a claude-code -a codex -a cursor -a github-copilot -a gemini-cli
```

Leave out `-g` to install into the current project instead of your home directory. Add `--skill ml-data-audit` to install only one skill.

### Copy once for most tools

Codex, Cursor, GitHub Copilot and Gemini CLI all read `~/.agents/skills/`. One copy there covers all four.

macOS and Linux:

```bash
mkdir -p ~/.agents/skills && cp -R ampba-skills/plugins/*/skills/* ~/.agents/skills/
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills"; Get-ChildItem ampba-skills\plugins\*\skills\* -Directory | Copy-Item -Destination "$HOME\.agents\skills" -Recurse -Force
```

For a single project, copy into `.agents/skills/` at the project root instead.

### Claude Code

Install as plugins. Updates arrive with `/plugin marketplace update`.

```
/plugin marketplace add moheetsubudhi-isb/ampba-skills
/plugin install optimization-toolkit@ampba-skills
/plugin install ml-toolkit@ampba-skills
```

Or copy the folders into `~/.claude/skills/` (every project) or `.claude/skills/` (one project):

```bash
mkdir -p ~/.claude/skills && cp -R ampba-skills/plugins/*/skills/* ~/.claude/skills/
```

Type `/` in Claude Code to see the installed skills.

### Codex and the ChatGPT desktop app

Copy the folders into `~/.agents/skills/` (every project) or `.agents/skills/` (one project). Codex picks a skill when a request matches its description; you can also run `/skills` or type `$` and the skill name to call it. See OpenAI's [Build skills guide](https://learn.chatgpt.com/docs/build-skills).

### Cursor

Copy the folders into `~/.cursor/skills/` or `~/.agents/skills/` (every project), or `.cursor/skills/` or `.agents/skills/` (one project). Cursor also reads `~/.claude/skills/`, so a Claude Code folder install works here too. Type `/` in Agent chat and search for the skill name to call it directly. See [Cursor's skills docs](https://cursor.com/docs/skills).

### GitHub Copilot in VS Code and Copilot CLI

Copy the folders into `~/.copilot/skills/` or `~/.agents/skills/` (every project), or `.github/skills/` or `.agents/skills/` (one project). Type `/skills` in Copilot Chat to confirm they loaded. See [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills).

### Gemini CLI

Copy the folders into `~/.gemini/skills/` or `~/.agents/skills/` (every project), or `.gemini/skills/` or `.agents/skills/` (one project). See [Gemini CLI Agent Skills](https://geminicli.com/docs/cli/skills/).

## Use in chat tools

Pasting this repository's link into a chat does not install anything. The assistant may read the page, but the skills will not load in later chats. Use the ready-made files in [`dist/`](dist) instead. Download the repository (Code > Download ZIP) and unzip it, or open a file in `dist/` on GitHub and select Download.

| File | Use it for |
|---|---|
| `dist/<skill>.zip` | Claude and ChatGPT |
| `dist/microsoft-365/<skill>.zip` | Microsoft 365 Copilot |
| `dist/text/<skill>.md` | Gemini Gems and any other chat. The skill and its reference notes in one file. |

Install one zip per skill you want. After installing, start a new chat and ask your question normally. If a skill does not load, name it in your request.

### Claude chat

Works on claude.ai and the desktop app, on Free, Pro, Max, Team and Enterprise plans.

1. Turn on **Code execution and file creation** in Settings > Capabilities. On Team and Enterprise, an owner turns on Skills in Organization settings first.
2. Go to **Customize > Skills** and upload `dist/<skill>.zip`.
3. Toggle the skill on.

See [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### ChatGPT

Skill upload is in beta and, at the time of writing, limited to business, enterprise and education workspaces. If you don't see **Skills** in the sidebar, your plan doesn't have it yet, or a workspace admin needs to allow uploads.

1. Go to **Skills**, select **Create**, then **Upload from your computer**.
2. Choose `dist/<skill>.zip` and confirm.
3. In a chat, type `@` to select the skill if it doesn't load by itself.

See [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt). On other plans, use the [text file](#any-other-chat) in a ChatGPT Project.

### Microsoft 365 Copilot

Skills are added to an agent built in Agent Builder. This is in preview for organisations in the Microsoft Frontier Program, and needs a Microsoft 365 Copilot licence.

1. In Copilot chat, select **Agents & Skills**, then open or create an agent.
2. Open **Configure**, expand **Skills** and select **Add**.
3. Upload `dist/microsoft-365/<skill>.zip`. This zip has `SKILL.md` at its top level, which Agent Builder requires. An agent holds up to eight skills.

Scripts run in a sandbox with no internet access and no package installs. The optimisation scripts need only Python. The ML scripts run only if `numpy`, `pandas` and `scikit-learn` are already in the sandbox; if they are not, the skill falls back to doing its checks by hand.

See [Add custom skills in Agent Builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills).

### Gemini app (Gems)

The Gemini app has no skill upload, but a Gem holds the same instructions.

1. Go to **Gems** > **New Gem** and give it the skill's name.
2. Paste the contents of `dist/text/<skill>.md` into **Instructions**. If it is too long, write "Follow the attached skill file for every request" instead and add the file under **Knowledge**.
3. Save, then chat with that Gem when you need the skill.

A Gem uses its skill only inside that Gem, and does not run the scripts.

### Any other chat

This covers the Microsoft Copilot app, ChatGPT without skill upload, Perplexity and others.

- **For a whole project:** paste `dist/text/<skill>.md` into a Project's instructions (ChatGPT Projects, Claude Projects), or attach it as a project file.
- **For one conversation:** attach or paste `dist/text/<skill>.md` at the start, then ask your question.

## Academic integrity

These skills are for work and learning. Don't use them for graded coursework wherever your course restricts AI-assisted work.

## Contributing

- Run `python tools/validate_skills.py` and every script's `--selftest` before committing. CI runs both, along with a secret scan.
- After changing a skill, run `python tools/build_bundles.py` and commit `dist/`. CI fails if the bundles are out of date.
- Keep frontmatter to `name` and `description` so skills stay portable.
- Refer to scripts and reference files by paths relative to the skill folder, and never name one assistant's tools. That keeps every skill working in every tool above.
- Encode the method, not the course material. Invent examples.
