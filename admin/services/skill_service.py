import os
import glob
import shutil
import threading
from pathlib import Path
from typing import Optional
import yaml

_lock = threading.Lock()


def _get_plugins_dir(repo_path: str) -> str:
    return os.path.join(repo_path, "plugins")


def _parse_skill_md(content: str) -> dict:
    """Split SKILL.md into frontmatter dict and body string."""
    if not content.startswith("---"):
        return {"frontmatter": {}, "body": content}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"frontmatter": {}, "body": content}
    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        frontmatter = {}
    body = parts[2].lstrip("\n")
    return {"frontmatter": frontmatter, "body": body}


def _write_skill_md(frontmatter: dict, body: str) -> str:
    """Serialize frontmatter dict and body into SKILL.md string."""
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).strip()
    return f"---\n{fm_str}\n---\n\n{body}\n"


def list_skills(repo_path: str) -> list:
    plugins_dir = _get_plugins_dir(repo_path)
    pattern = os.path.join(plugins_dir, "*", "skills", "*", "SKILL.md")
    results = []
    for path in glob.glob(pattern):
        parts = Path(path).parts
        try:
            skills_idx = next(i for i, p in enumerate(parts) if p == "skills")
            plugin_name = parts[skills_idx - 1]
            skill_name = parts[skills_idx + 1]
        except (StopIteration, IndexError):
            continue
        with open(path, encoding="utf-8") as f:
            parsed = _parse_skill_md(f.read())
        results.append({
            "plugin": plugin_name,
            "name": parsed["frontmatter"].get("name", skill_name),
            "description": parsed["frontmatter"].get("description", ""),
            "path": path,
            "frontmatter": parsed["frontmatter"],
        })
    return results


def get_skill(repo_path: str, plugin: str, skill: str) -> Optional[dict]:
    path = os.path.join(_get_plugins_dir(repo_path), plugin, "skills", skill, "SKILL.md")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        content = f.read()
    parsed = _parse_skill_md(content)
    return {
        "plugin": plugin,
        "skill": skill,
        "frontmatter": parsed["frontmatter"],
        "body": parsed["body"],
        "raw": content,
    }


def create_skill(repo_path: str, plugin: str, skill: str, frontmatter: dict, body: str) -> dict:
    skill_dir = os.path.join(_get_plugins_dir(repo_path), plugin, "skills", skill)
    os.makedirs(skill_dir, exist_ok=True)
    path = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(path):
        raise FileExistsError(f"Skill '{skill}' already exists in plugin '{plugin}'")
    content = _write_skill_md(frontmatter, body)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return get_skill(repo_path, plugin, skill)


def update_skill(repo_path: str, plugin: str, skill: str, frontmatter: dict, body: str) -> dict:
    path = os.path.join(_get_plugins_dir(repo_path), plugin, "skills", skill, "SKILL.md")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Skill '{skill}' not found in plugin '{plugin}'")
    content = _write_skill_md(frontmatter, body)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return get_skill(repo_path, plugin, skill)


def delete_skill(repo_path: str, plugin: str, skill: str) -> bool:
    skill_dir = os.path.join(_get_plugins_dir(repo_path), plugin, "skills", skill)
    if not os.path.exists(skill_dir):
        raise FileNotFoundError(f"Skill '{skill}' not found in plugin '{plugin}'")
    with _lock:
        shutil.rmtree(skill_dir)
    return True
