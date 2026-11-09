# Codex runtime adapter

Read this before a shared workflow in `commands/` or a specialist profile in `agents/`. These are Codex-specific translations of this plugin's instructions, not changes to the project's rules or the user's request. They take precedence over Claude-specific mechanics in the shared files. Keep the shared workflow's state ownership, evidence requirements, and verification gates.

## Paths and invocation

- Resolve the plugin root from the loaded skill's location: `skills/<name>/SKILL.md` is two directories below it. Use that installed package, which may be in a cache, rather than assuming this source checkout exists.
- In shared files, `${CLAUDE_PLUGIN_ROOT}` means that resolved plugin root. It is not a Codex environment variable. Resolve relative plugin references there; resolve project paths against the user's target repository.
- `/mynrd-*` in shared examples means the corresponding `$mynrd-*` skill in Codex. Use the name shown by the skill picker if it is namespaced. `$ARGUMENTS` means the user's text following the skill invocation, not a shell variable.
- Load only the command and specialist profiles needed for the current request. Never execute a Markdown command as a shell command.

## Tools and permissions

- `Read`, `Glob`, and `Grep` mean the available file-reading/search tools. Shell reads such as `Get-Content`, `rg`, or `cat` are allowed when no dedicated reader exists.
- `Edit` and `Write` mean the available file-editing tool, preferably `apply_patch`. Keep JSON valid and preserve fields owned by other workflow stages. The shared prohibition on shell file reads is Claude-specific and does not apply in Codex.
- `Bash` / `PowerShell` mean the available command runner with the correct shell for the host. `WebFetch` means available browsing when the task needs it. `AskUserQuestion` means an available question tool or a concise question to the user; do not invent tool names.
- `TodoWrite` is optional UI bookkeeping. Use a planning tool if available, otherwise a concise progress update. `progress.json` remains the persisted source of truth. Do not create a Codex goal merely to mirror the task list.
- Retain the session's sandbox, approval rules, and network limits. The skill never changes `approval_policy`, `sandbox_mode`, trust settings, or command allowlists. A plugin installation is not authorization to bypass them. Report permission blockers honestly and continue independent work.
- Give concise progress updates during long runs. The shared instruction to report only at the end means no unnecessary approval checkpoints, not silence until completion.
- Start local services through the available background/session mechanism, retain their process identity, and stop only services you started. On Windows use hidden windows for background helpers. Follow the shared readiness and cleanup rules.

## Specialist work

The Markdown files in `agents/` are the canonical Claude profiles. Matching native Codex definitions are generated into `codex-agents/*.toml`. Register them with the bundled `scripts/install_codex_agents.py --project <target-root>` (or `--user` when explicitly requested). `$mynrd-init` installs project agents; installing the plugin alone supplies skills and the installer. Ignore Claude frontmatter `tools`, `model`, and `effort`. Native definitions inherit the parent model and reasoning; never pass `sonnet`, `opus`, or `fable` to Codex.

For planning drafts or dispatch implementation:

1. Choose the profile from the shared dispatch table. Read its body and apply these tool/model translations.
2. If delegation is available and permitted, prefer the matching registered `mynrd-*` custom agent exposed by the runtime, or a project specialist covering the stack and returning `## Result`. Use the runtime's supported named-agent selection; never invent an `agent_type` argument on a tool that lacks it. If named selection is unavailable, pass the selected bundled profile and adapter to an available worker and report that fallback. Do not assume `.claude/agents/` is a Codex registry. Inherit the configured model unless the user or applicable project instructions explicitly choose another supported model.
3. Give the worker the exact AC, relevant plan notes, file ownership, conventions, exclusions, and any running service URL. Include the resolved profile path and this adapter, or their relevant contents if the worker cannot read them. Tell it that other agents may be working in the repository and that it must preserve their edits.
4. Workers do not write `.work/` state or run git mutations. Require the shared `## Result` report. Only the coordinator records progress, evaluates evidence, and stages/commits eligible work. Run overlapping ownership sequentially; parallelize only independent slices within runtime limits.
5. If delegation is unavailable or prohibited, say so once and execute slices sequentially in the current session using the same specialist guidance. Keep implementation, evidence evaluation, and state updates as distinct steps. Do not claim a subagent ran. Record the execution mode honestly in `runs[].notes` and leave `runs[].agents` empty when none ran.

The planning skill may use the docs profile for a read-only draft; it still stops after writing the plan. Dispatch keeps its existing local-commit rules, protected-branch restrictions, and no-push boundary. Never stage unrelated existing changes; if a task's file contains pre-existing user edits that cannot be safely separated, leave it uncommitted and explain why.

## Setup and help

For `$mynrd-init`, use the Codex skill's own setup instructions instead of `commands/mynrd-init.md`. Codex setup merges a scoped defaults block into the target project's `AGENTS.md`, adds `.work/` to `.gitignore`, and installs native agents in `.codex/agents/`; it does not write Claude settings or Codex global configuration.

For `$mynrd-help`, read `.help/INDEX.md` and `.help/codex.md` before other matched topics. Codex setup, invocation, agent selection, and permissions in that topic override Claude examples in the shared help. Preserve the read-only help boundary.
