# mynrd-ai-plugins

Personal AI plugin marketplace for [Claude Code](https://claude.com/claude-code) and Codex.

Everything here runs fully local: no issue tracker, no external services, no plugin credentials, no MCP server. Workflows write project files and local git commits. The explicit Codex user-agent installer also writes its six definitions and receipt into your Codex agents directory.

## Plugins

### mynrd-flow

A personal dev workflow toolkit that takes a raw request from "someone asked for this" to "built, tested, and verified by a human" - six workflows and six specialist profiles. Claude Code use slash commands; Codex uses skills with the same names (for example, `$mynrd-plan`).

| Command | What it does |
|---|---|
| `/mynrd-init` | One-time project setup: allowlist what the build loop needs in `.claude/settings.local.json` so `/mynrd-dispatch` runs without permission prompts, and write the workflow's default rules to `CLAUDE.local.md`. Merges, never overwrites. |
| `/mynrd-plan` | The entry point. Take a raw request (idea, bug report, chat blob), check `.work/` for existing work on it, discuss it, and write `PLAN.md` (Context, What needs to happen, Out of scope, Dependencies, Acceptance Criteria, Implementation notes, Testing) plus `progress.json` into `.work/<date>-<slug>/`. |
| `/mynrd-refine` | Refine a discussion thread into a formatted draft (Description + AC, or Repro Steps + AC for a bug). |
| `/mynrd-dispatch` | Run the build loop: dispatch acceptance criteria to specialist agents, run the test tiers named in the plan, commit per task, and loop until every AC is terminal. Records everything in `progress.json`. |
| `/mynrd-verified` | Record that you verified the green build yourself - closes the human-verification step in `progress.json`, stamps when, and keeps an optional one-line note of what you checked. |
| `/mynrd-help` | Answer questions about the plugin, grounded in its `.help/` knowledge base. |

**Specialist agents** (used by `/mynrd-dispatch`, also invocable directly):

- `mynrd-backend-dev` - .NET-first backend: ASP.NET Core, EF Core, SQL Server, Cosmos DB, Azure hosting
- `mynrd-front-dev` - Angular family (AngularJS to modern standalone/signals), Ionic/Capacitor, React
- `mynrd-node-dev` - Node.js / TypeScript: APIs, workers, CLIs, libraries, tooling
- `mynrd-python-dev` - Python: FastAPI/Django/Flask, CLIs, ETL, asyncio, MCP servers
- `mynrd-designer` - UI/UX and visual design, production markup/styles, accessibility
- `mynrd-docs-writer` - plan drafts for `/mynrd-plan`, and docs: README, help pages, runbooks, decision records, doc comments

Agents implement exactly the acceptance criteria they are handed. They never run git and never edit `progress.json` or `PLAN.md` - only the dispatch loop does.

## Install

Claude Code:

```
claude plugin marketplace add https://github.com/mynrd/ai-plugins.git
claude plugin install mynrd-flow@mynrd-ai-plugins
```

Codex (current CLI with plugin support):

```text
codex plugin marketplace add https://github.com/mynrd/ai-plugins.git
codex plugin add mynrd-flow@mynrd-ai-plugins
```

For an unpublished local checkout, run `codex plugin marketplace add .` from this repository root, then the same `codex plugin add` command. Open a new Codex session in your target project. Desktop users can install/enable `mynrd-flow` from the `mynrd AI Plugins` source in the Plugins Directory. Clients without `plugin add` can use the desktop flow or update Codex.

No environment variables or MCP server are needed. Claude's `/mynrd-init` configures its local allowlist. Codex's `$mynrd-init` instead merges workflow defaults into the target project's `AGENTS.md` and ignores `.work/`; `$mynrd-init check` only reports. It preserves existing instructions and test commands and does not change permission or model settings. `AGENTS.md` may be shared with your team; it is not automatically git-ignored.

Codex has native TOML definitions for the same six specialists. To make them available in every project, run this once from the checkout (Python 3.11+):

```text
python plugins/mynrd-flow/scripts/install_codex_agents.py --user
```

This installs into `~/.codex/agents/` (or `$CODEX_HOME/agents` when configured). For project-only agents, use `$mynrd-init` in that project or run the installer with `--project <project-root>`. Add `--check` for a read-only check. Re-run after updating the plugin; locally edited or conflicting files are preserved. Open a new Codex session, then ask, for example, `Use mynrd-python-dev to implement this Python change.`

Claude discovers the existing Markdown agents through its plugin; Codex discovers the installed TOML agents. Both derive from the same specialist instructions. Dispatch prefers a registered specialist, with a general-worker or sequential fallback when the runtime cannot select native agents. See [Codex setup and troubleshooting](plugins/mynrd-flow/.help/codex.md).

## Workflow

```
/mynrd-plan  →  /mynrd-dispatch  →  /mynrd-verified
   PLAN.md        build + test         human sign-off
```

Each stage writes to the project's `.work/<date>-<slug>/` folder. `/mynrd-refine` and `/mynrd-help` fit anywhere in between.

The `.work/<date>-<slug>/` folder is the plugin's only state: `PLAN.md` (what to build), `progress.json` (every AC, every test case, timestamps, blockers), `BUILD.md` (the dispatch handoff report, `BUILD_02.md` and up on later runs), and `REVISED_NN.md` (one per change asked for after the handoff). Its schema lives in `plugins/mynrd-flow/PROGRESS-SCHEMA.md`. The folder is meant to be git-ignored in your project (add `.work/` to your `.gitignore`); nothing else reads or writes it.

Dispatch ends at "development is done - try it now" and hands verification to you. `/mynrd-verified` is how you say it happened: it verifies nothing itself, it records your sign-off so a later session sees finished work instead of a step stuck in progress.

## Repo layout

```
.claude-plugin/marketplace.json   Claude Code marketplace manifest
.agents/plugins/marketplace.json Codex marketplace manifest
plugins/mynrd-flow/               The plugin
  plugin.json                     Portable plugin manifest
  .codex-plugin/plugin.json       Codex compatibility manifest
  skills/                         Six skill entry points
  adapters/codex.md               Codex tool, path, and agent translations
  commands/                       The six slash commands
  agents/                         Canonical specialist profiles / Claude agents
  codex-agents/                   Six generated native Codex TOML agents
  scripts/install_codex_agents.py User/project Codex agent installer
  .help/                          Knowledge base read by /mynrd-help
  PROGRESS-SCHEMA.md              The progress.json schema every command reads
```

## Maintainer checks

Use Python 3.11+. After editing `agents/*.md` or `adapters/codex-worker.md`, run `python scripts/generate_codex_agents.py`. Commit the generated `codex-agents/*.toml` alongside the source changes. Run `python scripts/validate_plugins.py` to check catalogs, aligned versions, skill references, agent coverage, and generated-file drift. Run `python -m unittest discover -s scripts/tests` to check installer behavior. All client manifests use the same release version. The shared `commands/`, `agents/`, and `PROGRESS-SCHEMA.md` remain the workflow sources; keep Codex differences in `adapters/` and the setup skill.

The skill wrappers also route back to the existing native command if a Claude Code client discovers them, so both entry paths use the same workflow. Validate installation in each client before publishing a release. Packaging follows the [official OpenAI plugin format](https://developers.openai.com/plugins/build/plugins).

## License

[MIT](LICENSE)
