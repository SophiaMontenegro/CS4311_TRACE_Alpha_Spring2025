from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from team1_router import team1_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # vite hosted here.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(team1_router)
