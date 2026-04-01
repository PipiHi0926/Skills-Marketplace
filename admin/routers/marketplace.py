import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
import main as app_main
from services import manifest_service

router = APIRouter()


@router.get("/marketplace")
def get_marketplace(repo_path: str = Depends(app_main.get_repo_path)):
    return manifest_service.read_marketplace(repo_path)


@router.post("/marketplace/sync")
def sync_marketplace(repo_path: str = Depends(app_main.get_repo_path),
                     _auth: HTTPAuthorizationCredentials = Depends(app_main.require_auth)):
    return manifest_service.sync_marketplace(repo_path)
