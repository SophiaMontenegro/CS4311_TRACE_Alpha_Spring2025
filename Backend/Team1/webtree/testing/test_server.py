from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Team1.webtree.routes import router  # Adjust this if needed

app = FastAPI()

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # use "*" if you want to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
