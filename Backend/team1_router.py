from fastapi import APIRouter
from Team1.webtree.routes import router as webtree_router
# Note for other teams, rename your Team directory without a space!

team1_router = APIRouter()
team1_router.include_router(webtree_router, prefix="/api/tree", tags=["Web Tree"])
