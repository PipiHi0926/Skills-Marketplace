import os
import re
from datetime import date
import threading

from services.manifest_service import read_marketplace, write_marketplace

_lock = threading.Lock()


def _bump_semver(version: str, bump_type: str) -> str:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        return "1.0.0"
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def bump_version(repo_path: str, plugin: str, bump_type: str, changelog_entry: str) -> dict:
    marketplace = read_marketplace(repo_path)
    plugins = marketplace.get("plugins", [])
    target = next((p for p in plugins if p["name"] == plugin), None)
    if target is None:
        raise ValueError(f"Plugin '{plugin}' not found in marketplace.json")
    old_version = target.get("version", "1.0.0")
    new_version = _bump_semver(old_version, bump_type)
    target["version"] = new_version
    marketplace["plugins"] = plugins
    write_marketplace(repo_path, marketplace)
    _append_changelog(repo_path, plugin, new_version, changelog_entry)
    return {"plugin": plugin, "old_version": old_version, "new_version": new_version}


def _append_changelog(repo_path: str, plugin: str, version: str, entry: str):
    changelog_path = os.path.join(repo_path, "plugins", plugin, "CHANGELOG.md")
    today = date.today().isoformat()
    new_section = f"\n## [{version}] - {today}\n### Changed\n- {entry}\n"
    with _lock:
        if os.path.exists(changelog_path):
            with open(changelog_path, encoding="utf-8") as f:
                existing = f.read()
            lines = existing.split("\n", 2)
            if len(lines) >= 2:
                content = lines[0] + "\n" + new_section + ("\n".join(lines[1:]) if len(lines) > 1 else "")
            else:
                content = existing + new_section
        else:
            content = f"# Changelog — {plugin}\n{new_section}"
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(content)


def get_changelog(repo_path: str, plugin: str) -> str:
    changelog_path = os.path.join(repo_path, "plugins", plugin, "CHANGELOG.md")
    if not os.path.exists(changelog_path):
        return ""
    with open(changelog_path, encoding="utf-8") as f:
        return f.read()
