import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from routers import skills, plugins, marketplace, versions

ADMIN_SECRET_TOKEN = os.getenv("ADMIN_SECRET_TOKEN", "changeme")
SKILLS_REPO_PATH = os.getenv("SKILLS_REPO_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="TSMC ISDD Skills Admin",
    description="Admin API for managing Claude Code skills marketplace",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_repo_path() -> str:
    return SKILLS_REPO_PATH


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None or credentials.credentials != ADMIN_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials


app.include_router(skills.router, prefix="/api", tags=["skills"])
app.include_router(plugins.router, prefix="/api", tags=["plugins"])
app.include_router(marketplace.router, prefix="/api", tags=["marketplace"])
app.include_router(versions.router, prefix="/api", tags=["versions"])

app.mount("/admin", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static", "admin"), html=True), name="admin")


@app.get("/health")
def health():
    return {"status": "ok", "repo_path": SKILLS_REPO_PATH}
