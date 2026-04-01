import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
import main as app_main
from services import skill_service
from models.skill import SkillCreateRequest, SkillUpdateRequest

router = APIRouter()


@router.get("/skills")
def list_skills(repo_path: str = Depends(app_main.get_repo_path)):
    return skill_service.list_skills(repo_path)


@router.get("/skills/{plugin}/{skill}")
def get_skill(plugin: str, skill: str, repo_path: str = Depends(app_main.get_repo_path)):
    result = skill_service.get_skill(repo_path, plugin, skill)
    if result is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return result


@router.post("/skills/{plugin}/{skill}")
def create_skill(plugin: str, skill: str, body: SkillCreateRequest,
                 repo_path: str = Depends(app_main.get_repo_path),
                 _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    try:
        return skill_service.create_skill(repo_path, plugin, skill, body.frontmatter, body.body)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/skills/{plugin}/{skill}")
def update_skill(plugin: str, skill: str, body: SkillUpdateRequest,
                 repo_path: str = Depends(app_main.get_repo_path),
                 _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    try:
        return skill_service.update_skill(repo_path, plugin, skill, body.frontmatter, body.body)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/skills/{plugin}/{skill}")
def delete_skill(plugin: str, skill: str,
                 repo_path: str = Depends(app_main.get_repo_path),
                 _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    try:
        skill_service.delete_skill(repo_path, plugin, skill)
        return {"deleted": True, "plugin": plugin, "skill": skill}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
