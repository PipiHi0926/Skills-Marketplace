import os
import json
import glob
import threading
from pathlib import Path
from typing import Optional

_lock = threading.Lock()


def _marketplace_path(repo_path: str) -> str:
    return os.path.join(repo_path, ".claude-plugin", "marketplace.json")


def _plugin_json_path(repo_path: str, plugin: str) -> str:
    return os.path.join(repo_path, "plugins", plugin, ".claude-plugin", "plugin.json")


def read_marketplace(repo_path: str) -> dict:
    path = _marketplace_path(repo_path)
    if not os.path.exists(path):
        return {"name": "tsmc-isdd-skills", "plugins": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_marketplace(repo_path: str, data: dict) -> dict:
    path = _marketplace_path(repo_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return data


def read_plugin_json(repo_path: str, plugin: str) -> Optional[dict]:
    path = _plugin_json_path(repo_path, plugin)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_plugin_json(repo_path: str, plugin: str, data: dict) -> dict:
    path = _plugin_json_path(repo_path, plugin)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return data


def list_plugins(repo_path: str) -> list:
    plugins_dir = os.path.join(repo_path, "plugins")
    if not os.path.exists(plugins_dir):
        return []
    result = []
    for entry in os.scandir(plugins_dir):
        if not entry.is_dir():
            continue
        plugin_data = read_plugin_json(repo_path, entry.name) or {}
        skills = _list_plugin_skills(repo_path, entry.name)
        result.append({
            "name": entry.name,
            "description": plugin_data.get("description", ""),
            "keywords": plugin_data.get("keywords", []),
            "skills": skills,
        })
    return result


def _list_plugin_skills(repo_path: str, plugin: str) -> list:
    pattern = os.path.join(repo_path, "plugins", plugin, "skills", "*", "SKILL.md")
    return [Path(p).parent.name for p in glob.glob(pattern)]


def sync_marketplace(repo_path: str) -> dict:
    marketplace = read_marketplace(repo_path)
    existing = {p["name"]: p for p in marketplace.get("plugins", [])}
    plugins_dir = os.path.join(repo_path, "plugins")
    new_plugins = []
    if os.path.exists(plugins_dir):
        for entry in os.scandir(plugins_dir):
            if not entry.is_dir():
                continue
            plugin_data = read_plugin_json(repo_path, entry.name) or {}
            prev = existing.get(entry.name, {})
            new_plugins.append({
                "name": entry.name,
                "source": f"./plugins/{entry.name}",
                "description": plugin_data.get("description", prev.get("description", "")),
                "version": prev.get("version", "1.0.0"),
                "category": prev.get("category", "general"),
                "keywords": plugin_data.get("keywords", prev.get("keywords", [])),
            })
    marketplace["plugins"] = new_plugins
    write_marketplace(repo_path, marketplace)
    return {"plugins_found": len(new_plugins), "marketplace": marketplace}


def create_plugin(repo_path: str, name: str, description: str, category: str = "general", keywords: list = None) -> dict:
    plugin_data = {
        "name": name,
        "description": description,
        "author": {"name": "ISDD Platform Team"},
        "keywords": keywords or [],
    }
    write_plugin_json(repo_path, name, plugin_data)
    skills_dir = os.path.join(repo_path, "plugins", name, "skills")
    os.makedirs(skills_dir, exist_ok=True)
    marketplace = read_marketplace(repo_path)
    plugins = marketplace.get("plugins", [])
    if not any(p["name"] == name for p in plugins):
        plugins.append({
            "name": name,
            "source": f"./plugins/{name}",
            "description": description,
            "version": "1.0.0",
            "category": category,
            "keywords": keywords or [],
        })
        marketplace["plugins"] = plugins
        write_marketplace(repo_path, marketplace)
    return plugin_data
