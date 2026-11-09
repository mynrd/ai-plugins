"""Install bundled native agents into Codex's user or project registry.

Python 3.11+, no dependencies. Conflicting or locally edited files are preserved.
"""

import argparse
import hashlib
import json
import os
import sys
import tomllib
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
RECEIPT = ".mynrd-flow-agents.json"


def digest(content):
    return hashlib.sha256(content).hexdigest()


def install(destination, check=False):
    sources = sorted((PLUGIN / "codex-agents").glob("*.toml"))
    if len(sources) != 6:
        raise ValueError("Expected six bundled native Codex agents")
    receipt_path = destination / RECEIPT
    if receipt_path.is_symlink():
        raise ValueError(f"Refusing symlink receipt: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
    if not isinstance(receipt, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in receipt.items()):
        raise ValueError(f"Invalid installation receipt: {receipt_path}")
    operations = []
    for source in sources:
        content = source.read_bytes()
        agent = tomllib.loads(content.decode("utf-8"))
        if agent.get("name") != source.stem or not all(agent.get(k) for k in ("description", "developer_instructions")):
            raise ValueError(f"Invalid agent: {source}")
        target = destination / source.name
        if target.is_symlink():
            status = "conflict"
        elif not target.exists():
            status = "missing"
        else:
            current = target.read_bytes()
            status = "ok" if current == content else "outdated" if digest(current) == receipt.get(source.name) else "conflict"
        operations.append((target, content, status))
        print(f"{status}: {target}")
    if any(status == "conflict" for _, _, status in operations):
        print("Conflicting files preserved; no files changed. Choose another scope or reconcile them manually.", file=sys.stderr)
        return 1
    if check:
        return int(any(status != "ok" for _, _, status in operations))
    destination.mkdir(parents=True, exist_ok=True)
    for target, content, status in operations:
        if status != "ok":
            target.write_bytes(content)
    receipt_path.write_text(json.dumps({p.name: digest(c) for p, c, _ in operations}, indent=2) + "\n", encoding="utf-8")
    print("Installed six Codex agents. Start a new Codex session to discover them.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--user", action="store_true", help="Install in CODEX_HOME/agents or ~/.codex/agents")
    scope.add_argument("--project", type=Path, metavar="ROOT", help="Install in ROOT/.codex/agents")
    parser.add_argument("--check", action="store_true", help="Read-only; return nonzero when missing, outdated, or conflicting")
    args = parser.parse_args()
    base = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") if args.user else args.project.expanduser() / ".codex"
    try:
        return install(base.resolve() / "agents", args.check)
    except (OSError, ValueError) as error:
        print(f"Agent installation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
