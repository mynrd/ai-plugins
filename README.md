# mynrd-ai-plugins

Personal AI plugin marketplace for [Claude Code](https://claude.com/claude-code) and Cursor.

Everything here runs fully local: no issue tracker, no external services, no credentials, no MCP server. The only things the plugins ever write are files inside your repo (`.work/` state plus the source edits you asked for) and local git commits.

## Plugins

### mynrd-flow

A personal dev workflow toolkit that takes a raw request from "someone asked for this" to "built, tested, and verified by a human" - five slash commands and five specialist implementation agents.

| Command | What it does |
|---|---|
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

Agents implement exactly the acceptance criteria they are handed. They never run git and never edit `progress.json` or `PLAN.md` - only the dispatch loop does.

## Install

Claude Code:

```
claude plugin marketplace add https://github.com/mynrd/ai-plugins.git
claude plugin install mynrd-flow@mynrd-ai-plugins
```

Cursor: the repo ships a `.cursor-plugin/marketplace.json` manifest; add this repo as a plugin source the same way.

No environment variables, no MCP server, no further setup.

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
.cursor-plugin/marketplace.json   Cursor marketplace manifest
plugins/mynrd-flow/               The plugin
  commands/                       The five slash commands
  agents/                         The five specialist agents
  .help/                          Knowledge base read by /mynrd-help
  PROGRESS-SCHEMA.md              The progress.json schema every command reads
```

## License

[MIT](LICENSE)
