"""Validate the repository's plugin catalogs and packaged skill references.

Run with Python 3.10+ from any directory. No third-party dependencies required.
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "mynrd-flow"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def confined_path(root, value):
    assert value.startswith("./"), f"Expected ./-relative path: {value}"
    path = (root / value).resolve()
    assert path.is_relative_to(root.resolve()), f"Path escapes package: {value}"
    assert path.exists(), f"Missing path: {path}"
    return path


def main():
    portable = read_json(PLUGIN / "plugin.json")
    assert portable["name"] == "mynrd-flow"
    assert portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    for client in ("claude", "cursor", "codex"):
        manifest = read_json(PLUGIN / f".{client}-plugin" / "plugin.json")
        assert (manifest["name"], manifest["version"]) == (portable["name"], portable["version"])
        if client == "codex":
            catalog_path = ROOT / ".agents" / "plugins" / "marketplace.json"
            assert confined_path(PLUGIN, manifest["skills"]) == PLUGIN / "skills"
        else:
            catalog_path = ROOT / f".{client}-plugin" / "marketplace.json"
        catalog = read_json(catalog_path)
        assert catalog["name"] == "mynrd-ai-plugins"
        entries = [entry for entry in catalog["plugins"] if entry["name"] == portable["name"]]
        assert len(entries) == 1, f"Expected one plugin entry in {catalog_path}"
        entry = entries[0]
        source = entry["source"]
        if isinstance(source, dict):
            assert source["source"] == "local"
            source = source["path"]
            assert entry["policy"]["installation"] == "AVAILABLE"
            assert entry["policy"]["authentication"] == "ON_INSTALL"
            assert entry["category"] == "Productivity"
        if "version" in entry:
            assert entry["version"] == portable["version"]
        assert confined_path(ROOT, source) == PLUGIN

    commands = {path.stem for path in (PLUGIN / "commands").glob("*.md")}
    skills = list((PLUGIN / "skills").glob("*/SKILL.md"))
    assert {path.parent.name for path in skills} == commands, "Command/skill coverage differs"
    links = 0
    for path in skills:
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"Missing frontmatter: {path}"
        frontmatter = content.split("---", 2)[1]
        assert re.search(rf"^name: {re.escape(path.parent.name)}$", frontmatter, re.M)
        assert re.search(r"^description: \S.+$", frontmatter, re.M)
        for target in re.findall(r"\]\(([^)]+)\)", content):
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_relative_to(PLUGIN.resolve()), f"Reference escapes package: {target}"
            assert resolved.is_file(), f"Missing skill reference: {resolved}"
            links += 1
    profiles = list((PLUGIN / "agents").glob("mynrd-*.md"))
    assert len(profiles) == 6
    print(f"Validated 3 catalogs, 4 manifests, {len(skills)} skills, {links} skill links, and 6 specialist profiles.")


if __name__ == "__main__":
    main()
