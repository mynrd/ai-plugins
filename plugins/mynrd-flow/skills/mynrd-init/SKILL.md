---
name: mynrd-init
description: Set up or check mynrd-flow defaults in the current Codex project, preserving existing instructions and permissions. Use when the user asks to initialize this workflow; check reports without writing.
---

# mynrd-init

In Claude Code, read and follow [the existing setup command](../../commands/mynrd-init.md) using that client's native behavior. The instructions below apply to Codex only.

Read [the Codex adapter](../../adapters/codex.md). This setup is optional; every other skill works without it.

1. Resolve the target repository root with `git rev-parse --show-toplevel`, falling back to the current directory. State the path. Read its `AGENTS.md`, any `AGENTS.override.md`, and `.gitignore` if present. Discover unit/UI test commands from project files without running tests.
2. With the argument `check`, report which items below are present, missing, or need attention. Run the bundled [agent installer](../../scripts/install_codex_agents.py) with `--project <target-root> --check`; this is read-only, and a nonzero exit means attention is needed. Then stop without writes. An unknown setup argument gets a usage explanation, not a write.
3. With no argument, merge the managed block below into `AGENTS.md`: create the file if absent, append if neither marker exists, or replace the one complete matching block. Preserve all text outside it. Preserve user-customized test commands; fill only empty or `none found` values. Duplicate, reversed, or unmatched markers require attention: do not rewrite that file.
4. An existing nonempty `AGENTS.override.md` takes precedence over `AGENTS.md` in Codex. If present, report that setup cannot ensure the defaults are loaded, leave both instruction files unchanged, and explain that the user can choose where to merge the block. Do not create an override file, since it could hide the project's existing instructions.
5. In a git repository, ensure `.gitignore` covers `.work/`, appending the entry only when needed. Do not ignore `AGENTS.md` automatically: it is a normal project instruction file that may be shared with the team. Outside git, skip the ignore step. Never commit, untrack files, or modify global configuration.
6. With no argument, run the bundled [agent installer](../../scripts/install_codex_agents.py) using Python 3.11+ and `--project <target-root>`. Resolve the script from this installed skill's plugin root. It installs six native TOML definitions into `.codex/agents/` and records managed hashes there. It preserves unrelated agents and refuses to overwrite locally edited or conflicting definitions. Report conflicts or missing Python without working around them. Never use `--user` implicitly. Project definitions may be committed with the project; do not ignore them automatically.
7. Report each item's status (`ok`, `created`, `updated`, `skipped`, or `needs attention`), actual test commands discovered, agent installation results, and any write failures. Do not start planning or building. Recommend a new Codex session to discover changed instructions and agents.

Managed block (substitute discovered test commands):

```markdown
<!-- mynrd-flow:codex:start -->
## mynrd-flow in Codex

These defaults apply when using the mynrd-flow skills. They do not require unrelated work to use this workflow.

- Use `$mynrd-plan` to create or revise `.work/<date>-<slug>/PLAN.md` and `progress.json`. Planning stops before implementation.
- Use `$mynrd-dispatch` to build an existing plan, gather test/live/review evidence, and record progress. Follow the installed skill's Codex adapter for specialist delegation and its sequential fallback.
- Keep the session's configured model, permissions, sandbox, and project instructions. Setup does not grant broader access.
- Dispatch stages only its own changes and commits green tasks on eligible feature branches. Never push or rewrite history; never bypass hooks. No commits on main, master, dev, develop, release/*, or hotfix/*.
- Green tests are not human verification. Use `$mynrd-verified` only when the user says they exercised the work and want that recorded.
- Unit tests: none found
- UI tests: none found
<!-- mynrd-flow:codex:end -->
```

The block refers to installed skill names, not a versioned plugin cache path. Re-running setup must not duplicate it. Read or write failures are reported without overwriting unreadable content.
