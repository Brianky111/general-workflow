# Repository Guidelines

## Project Structure & Module Organization

This repository is for developing a reusable Codex skill for general development workflows. The file `通用开发工作流-v3.8-环节拆分版.md` is source material for the skill, not a process that this repository itself must follow. Keep the eventual skill package small and explicit:

```text
<skill-name>/
├── SKILL.md              # required trigger metadata and core instructions
├── agents/openai.yaml    # optional UI metadata
├── references/           # longer workflow details loaded only when needed
├── scripts/              # deterministic helpers or validators
└── assets/               # output templates or static resources, if needed
```

Use `references/` for detailed workflow text; keep `SKILL.md` focused on when to use the skill and the minimum procedure an agent must follow.

## Build, Test, and Development Commands

There is no application build system in this checkout. Useful local checks:

```powershell
Get-ChildItem -Force
Select-String -Path *.md -Pattern '^#{1,4}\s+'
git diff --check
```

After a skill folder exists, validate it with the Skill Creator validator:

```powershell
python "<path-to-skill-creator>\scripts\quick_validate.py" <skill-folder>
```

Run any scripts under `scripts/` directly before committing changes to them.

## Coding Style & Naming Conventions

Write Markdown in UTF-8. Skill folder names must be lowercase hyphen-case, for example `general-workflow`. In `SKILL.md`, include only YAML frontmatter fields `name` and `description`; make the description broad enough to trigger the skill in the right situations. Prefer imperative, concise instructions. Use fenced code blocks with language labels such as `powershell`, `json`, or `markdown`.

## Testing Guidelines

Validate three things before review: frontmatter loads, instructions are concise enough for agent use, and reference files are discoverable from `SKILL.md`. For substantial edits, forward-test with realistic prompts such as “Use this skill to plan a new feature workflow” and revise based on where the agent hesitates or loads too much context.

## Commit & Pull Request Guidelines

No Git history is available in this checkout. Use clear Conventional Commit-style messages such as `docs(skill): refine trigger guidance`, `feat(skill): add validation script`, or `test(skill): add forward-test prompt`. Pull requests should summarize the skill behavior change, list affected files, include validation commands run, and note any trigger behavior changes.

## Security & Configuration Tips

Do not store secrets, credentials, private host details, or project-specific business data in this skill. Keep examples generic so the skill remains reusable across repositories.
