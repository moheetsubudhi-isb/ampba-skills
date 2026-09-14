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

## Install

**Claude Code**
```
/plugin marketplace add moheetsubudhi-isb/ampba-skills
/plugin install optimization-toolkit@ampba-skills
/plugin install ml-toolkit@ampba-skills
```

**Codex, and the ChatGPT desktop app.** Copy a skill folder, such as `plugins/optimization-toolkit/skills/logical-constraints`, into `~/.agents/skills/` to use it everywhere, or into `.agents/skills/` inside one project. See OpenAI's [Build skills guide](https://learn.chatgpt.com/docs/build-skills).

Optimisation scripts need only Python 3. ML scripts also need `numpy`, `pandas` and `scikit-learn` (`pip install -r requirements.txt`).

## Use in the Claude or ChatGPT chat window

Pasting this repository's link into a chat does not install anything. The assistant may read the page, but the skills will not load by themselves in later chats. Install each skill once instead. While this repository is private, only people you add as collaborators can open the link or download it.

1. Download the repository (Code > Download ZIP) and unzip it.
2. Zip the one skill folder you want, so the folder is at the top of the zip:
   ```
   cd plugins/ml-toolkit/skills
   zip -r ml-data-audit.zip ml-data-audit
   ```
3. Upload the zip:
   - **Claude (claude.ai or the desktop app):** turn on *Code execution and file creation* in Settings > Capabilities, then upload in Customize > Skills. Works on Free, Pro, Max, Team and Enterprise plans.
   - **ChatGPT:** go to Skills > Create > Upload from your computer.
4. Start a new chat and ask your question normally. If the skill does not load, name it in your request.

The scripts inside a skill run only where the chat can execute code. Without that, the skill still guides the method and the assistant does the checks by reasoning.

**Quick one-off:** paste the text of a skill's `SKILL.md` into the chat, or into a Claude Project or ChatGPT Project's instructions. This works for that chat or project only.

## Academic integrity

These skills are for work and learning. Don't use them for graded coursework wherever your course restricts AI-assisted work.

## Contributing

- Run `python tools/validate_skills.py` and every script's `--selftest` before committing. CI runs both, along with a secret scan.
- Keep frontmatter to `name` and `description` so skills stay portable.
- Encode the method, not the course material. Invent examples.
