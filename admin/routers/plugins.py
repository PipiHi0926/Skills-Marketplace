import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
import main as app_main
from services import manifest_service
from models.plugin import PluginCreateRequest, PluginUpdateRequest

router = APIRouter()


@router.get("/plugins")
def list_plugins(repo_path: str = Depends(app_main.get_repo_path)):
    return manifest_service.list_plugins(repo_path)


@router.post("/plugins")
def create_plugin(body: PluginCreateRequest,
                  repo_path: str = Depends(app_main.get_repo_path),
                  _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    return manifest_service.create_plugin(
        repo_path, body.name, body.description, body.category, body.keywords
    )


@router.put("/plugins/{plugin}")
def update_plugin(plugin: str, body: PluginUpdateRequest,
                  repo_path: str = Depends(app_main.get_repo_path),
                  _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    existing = manifest_service.read_plugin_json(repo_path, plugin)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin}' not found")
    if body.description is not None:
        existing["description"] = body.description
    if body.keywords is not None:
        existing["keywords"] = body.keywords
    return manifest_service.write_plugin_json(repo_path, plugin, existing)
