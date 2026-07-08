# Project Identification

## Purpose

Decide whether the work is a new project, an old project, or a new module inside an old project. This controls how much code scanning is required later.

## Entry Conditions

- No `00-项目识别.md` exists for the feature, or it is incomplete.
- The agent cannot tell whether existing code must be preserved, extended, or ignored.

## Actions

1. Inspect repository structure, package manifests, existing docs, and obvious entry points.
2. Classify the work as:
   - `new-project`: no existing behavior to preserve.
   - `old-project`: existing behavior may be affected.
   - `new-module-in-old-project`: new area, but shared conventions still apply.
3. Record relevant files and areas that the interface/conflict stages must revisit.
4. Avoid making final conflict conclusions here.

## Output

Create or update `docs/features/<feature>/00-项目识别.md` with:

- conclusion,
- evidence read,
- areas requiring later code scan,
- explicit non-goals for this stage.

## Stop Conditions

Stop and ask the user if classification changes implementation risk or project scope.
