from fastapi import APIRouter
from Team1.webtree.routes import router as webtree_router
from Team1.httpclient.routes import router as httpclient_router
from Team1.intrudertool.routes import router as intruder_router


# Note for other teams, rename your Team directory without a space!

team1_router = APIRouter()
team1_router.include_router(webtree_router, prefix="/api/tree", tags=["Web Tree"])
team1_router.include_router(httpclient_router, prefix="/api/http", tags=["HTTP Tester"])
team1_router.include_router(intruder_router, prefix="/api/intruder", tags=["Intruder Tool"])
