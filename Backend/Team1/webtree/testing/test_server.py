# testing/test_server.py

from fastapi import FastAPI
from Team1.webtree.routes import router  # Adjust this if your path is different

app = FastAPI()
app.include_router(router)
