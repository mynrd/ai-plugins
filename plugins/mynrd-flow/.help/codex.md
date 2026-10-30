# Codex

mynrd-flow supports Codex alongside Claude Code and Cursor in the same repository. Codex exposes six skills with the same workflow names. The shared commands, specialist profiles, help, and progress schema ship together in one plugin package.

## Install

With a current Codex CLI that provides `codex plugin add`:

```text
codex plugin marketplace add https://github.com/mynrd/ai-plugins.git
codex plugin add mynrd-flow@mynrd-ai-plugins
```

To test a checkout before publishing, run these from this repository's root instead:

```text
codex plugin marketplace add .
codex plugin add mynrd-flow@mynrd-ai-plugins
```

Open a new Codex session in the project you want to work on. For desktop clients, select the `mynrd AI Plugins` marketplace in the Plugins Directory and install/enable `mynrd-flow`. If the CLI lacks `plugin add`, use that supported desktop installation flow or update Codex. No MCP connection or plugin credentials are needed.

The marketplace is `.agents/plugins/marketplace.json`; paths in it resolve from the repository root. Codex installs a cached copy of the plugin. Editing this source checkout does not necessarily refresh an installed copy: refresh the marketplace and reinstall the plugin, then start a new session. Avoid installing both the legacy and Codex catalog as separate copies of the same plugin.

## Use

| Skill | Input / outcome |
| --- | --- |
| `$mynrd-init` | Merge workflow defaults into the target project's `AGENTS.md`, discover test commands, and ignore `.work/`. Add `check` for a read-only report. |
| `$mynrd-plan <request or folder>` | Discuss the request and write or revise `PLAN.md` and `progress.json`. Stops before building. |
| `$mynrd-refine <discussion>` | Produce a work/bug draft and acceptance criteria in chat. Save `DRAFT.md` only when asked. |
| `$mynrd-dispatch <slug or folder>` | Build an existing plan, verify evidence, and commit eligible green tasks locally. Never pushes. |
| `$mynrd-verified <slug or folder> [note]` | Record that you exercised the finished work yourself. Never inferred from passing tests. |
| `$mynrd-help <question>` | Answer from bundled help without running workflows. |

Use the name shown in Codex's skill picker if it includes a plugin namespace. The `/mynrd-*` notation elsewhere in the help describes the equivalent Claude/Cursor commands; use skills in Codex.

## Setup and permissions

Codex setup is optional and safe to re-run. It owns only the `mynrd-flow:codex` managed block in `AGENTS.md` and the missing `.work/` ignore entry. Text outside the markers and custom test commands are preserved. Unlike Claude's personal `CLAUDE.local.md`, `AGENTS.md` is a normal project file that may be shared with your team; setup does not ignore it automatically.

An existing nonempty `AGENTS.override.md` may hide `AGENTS.md`. Setup reports this and leaves the instruction files unchanged so you can decide where the defaults belong. Malformed or duplicate managed markers are also reported without replacement.

Setup does not write `.claude/settings.local.json`, `.codex/config.toml`, model settings, command allowlists, or global files. Codex retains its normal approval and sandbox behavior; this plugin cannot promise a prompt-free session. A new session loads changed project instructions.

## Specialist execution

Dispatch uses the same six profiles under `agents/`. They are guidance, not automatically registered Codex agent types. When delegation is available and permitted, it uses a compatible runtime/project agent or passes the selected profile to an available worker. Workers inherit configured models; the Claude `sonnet`/`opus` settings are ignored.

If delegation is unavailable, the coordinator follows the same profiles sequentially and reports that mode. It does not pretend subagents ran. The coordinator alone updates `.work/`, evaluates AC evidence, and performs eligible local commits. Workers preserve one another's edits and cannot mutate git or workflow state.

## Troubleshooting

- **Skills missing:** confirm `mynrd-flow` is installed/enabled, open a new session, and inspect `codex plugin list`. Merely adding a marketplace does not install the plugin.
- **Changes not picked up:** refresh the marketplace, reinstall, and open a new session; the runtime reads its cached package.
- **Claude tool/model names appear:** use the skill entry point, which loads `adapters/codex.md` before the shared command. Do not execute `commands/*.md` directly in Codex without that adapter.
- **Permission prompt:** honor the session's approval flow. `$mynrd-init` does not disable it.
- **Missing plan or invalid progress:** use the shared workflow's refusal/re-plan path. Do not reconstruct history or mark verification green to bypass a gate.

The authoritative Codex instructions are `skills/*/SKILL.md` and `adapters/codex.md`; shared state rules remain in `PROGRESS-SCHEMA.md`.
