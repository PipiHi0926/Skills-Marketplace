import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
import main as app_main
from services import version_service

router = APIRouter()


class BumpRequest(BaseModel):
    bump_type: str = "patch"
    changelog_entry: str = ""


@router.post("/versions/{plugin}/bump")
def bump_version(plugin: str, body: BumpRequest,
                 repo_path: str = Depends(app_main.get_repo_path),
                 _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    try:
        return version_service.bump_version(repo_path, plugin, body.bump_type, body.changelog_entry)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/versions/{plugin}/history")
def get_changelog(plugin: str, repo_path: str = Depends(app_main.get_repo_path)):
    content = version_service.get_changelog(repo_path, plugin)
    return {"plugin": plugin, "changelog": content}
