from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import logging
import uvicorn
import strawberry
import os
import json
from typing import List, Optional

# Cralwer Routers and Services
from Team7.src.modules.crawler.service.crawler_service_router import get_service_routers as get_crawler_routers
from Team7.src.modules.crawler.service.crawler_service_router import get_websocket_handlers as get_crawler_websocket_handlers
from Team7.src.modules.crawler.service.crawler_service import job_results as crawler_job_results, running_jobs as crawler_running_jobs

# ML Routers and Services
from Team7.src.modules.ai.service.ml_service_router import get_service_routers as get_ml_router
from Team7.src.modules.ai.service.ml_service_router import get_websocket_handlers as get_ml_websocket_handlers
from Team7.src.modules.ai.service.ml_service import job_results as ml_job_results, running_jobs as ml_running_jobs

# Fuzzer Routers and Services
from Team7.src.modules.fuzzer.service.fuzzer_service_router import get_service_routers as gett_fuzzer_routers
from Team7.src.modules.fuzzer.service.fuzzer_service_router import get_websocket_handlers as get_fuzzer_websocket_handlers
from Team7.src.modules.fuzzer.service.fuzzer_service import job_results as fuzzer_job_results
from Team7.src.modules.fuzzer.service.fuzzer_service import running_jobs as fuzzer_running_jobs

# DBF Routers and Services
from Team7.src.modules.dbf.service.dbf_service_router import get_service_routers as get_dbf_routers
from Team7.src.modules.dbf.service.dbf_service_router import get_websocket_handlers as get_dbf_websocket_handlers
from Team7.src.modules.dbf.service.dbf_service import job_results as dbf_job_results, running_jobs as dbf_running_jobs

from team1_router import team1_router

from Team3.Database.team3_router import team3_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GraphQL Schema Definitions
@strawberry.type
class CrawlerResultType:
    id: int
    url: str
    parentUrl: Optional[str] = None
    title: str
    wordCount: int
    charCount: int
    linksFound: int
    error: bool

@strawberry.type
class DBFResultType:
    id: int
    url: str
    status: int
    payload: str
    length: int
    error: bool

@strawberry.type
class CredentialType:
    id: int
    username: str
    username_score: float
    password: str
    is_secure: bool
    password_evaluation: str

@strawberry.type
class FuzzerResultType:
    id: int
    response: int
    lines: int
    words: int
    chars: int
    payload: str
    length: int
    error: bool

@strawberry.type
class JobStatus:
    job_id: str
    status: str
    progress: float
    urls_processed: int
    total_urls: int
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    def get_crawler_results(self, job_id: str) -> List[CrawlerResultType]:
        if job_id in crawler_job_results and 'result_file' in crawler_job_results[job_id]:
            result_file = crawler_job_results[job_id]['result_file']

            if os.path.exists(result_file):
                try:
                    with open(result_file, 'r') as file:
                        data = json.load(file)
                        return [
                            CrawlerResultType(
                                id=index,
                                url=item['url'],
                                title=item['title'],
                                parentUrl=item.get('parentUrl'),
                                wordCount=item['wordCount'],
                                charCount=item['charCount'],
                                linksFound=item['linksFound'],
                                error=item['error'],
                            ) for index, item in enumerate(data)
                        ]
                except Exception as e:
                    logger.error(f'Error reading crawler results: {e}')
                    return []
        return []
    
    @strawberry.field
    def get_dbf_results(self, job_id: str) -> List[DBFResultType]:
        if job_id in dbf_job_results and 'results_file' in dbf_job_results[job_id]:
            results_file = dbf_job_results[job_id]['results_file']

            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as file:
                        data = json.load(file)
                        return [
                            DBFResultType(
                                id=item.get('id', index),
                                url=item['url'],
                                status=item['status'],
                                payload=item['payload'],
                                length=item['length'],
                                error=item['erro']
                            ) for index, item in enumerate(data)
                        ]
                except Exception as e:
                    logger.error(f'Error reading DBF results: {e}')
                    return []
        return []
    
    @strawberry.field
    def get_ml_results(self, job_id: str) -> List[CredentialType]:
        if job_id in ml_job_results and 'results_file' in ml_job_results[job_id]:
            result_file = ml_job_results[job_id]['results_file']

            if os.path.exists(result_file):
                try:
                    with open(result_file, 'r') as file:
                        data = json.load(file)
                        return [
                            CredentialType(
                                id=item['id'],
                                username=item['username'],
                                username_score=item['username_score'],
                                password=item['password'],
                                is_secure=item['is_secure'],
                                password_evaluation=item['password_evaluation'],
                            ) for item in data
                        ]
                except Exception as e:
                    logger.error(f'Error reading ML results: {e}')
                    return []
        return []
    
    @strawberry.field
    def get_fuzzer_results(self, job_id: str) -> List[FuzzerResultType]:
        if job_id in fuzzer_job_results and 'results_file' in fuzzer_job_results[job_id]:
            results_file = fuzzer_job_results[job_id]['results_file']

            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as file:
                        data = json.load(file)
                        return [
                            FuzzerResultType(
                                id=item['id'],
                                response=item['response'],
                                lines=item['lines'],
                                words=item['words'],
                                chars=item['chars'],
                                payload=item['payload'],
                                length=item['length'],
                                error=item['error'],
                            ) for item in data
                        ]
                
                except Exception as e:
                    logger.error(f'Error reading fuzzer results: {e}')
                    return []
                
        return []
    
    @strawberry.field
    def get_crawler_job_status(self, job_id: str) -> str:
        if job_id in crawler_running_jobs:
            return crawler_running_jobs[job_id]['status']
        if job_id in crawler_job_results:
            return 'completed'
        return 'not found'
    
    @strawberry.field
    def get_dbf_job_status(self, job_id: str) -> str:
        if job_id in dbf_running_jobs:
            return dbf_running_jobs[job_id]['status']
        if job_id in dbf_job_results:
            return 'completed'
        return 'not found'
    
    @strawberry.field
    def get_ml_job_status(self, job_id: str) -> str:
        if job_id in ml_running_jobs:
            return ml_running_jobs[job_id]['status']
        if job_id in ml_job_results:
            return 'completed'
        return 'not found'

    @strawberry.field
    def get_fuzzer_job_status(self, job_id: str) -> str:
        if job_id in fuzzer_running_jobs:
            return fuzzer_running_jobs[job_id]['status']
        if job_id in fuzzer_job_results:
            return 'completed'
        return 'not found'
    
schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

# Create FastAPI App
app = FastAPI(title='Trace API')

# config CORS to allow request from SveltKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include GraphQL router
app.include_router(graphql_app, prefix='/graphql')

app.include_router(team1_router)
app.include_router(team3_router)

# Register service routers
# Crawler routers
for router in get_crawler_routers():
    app.include_router(router)

# # DBF routers
for router in get_dbf_routers():
    app.include_router(router)

# ML router
for router in get_ml_router():
    app.include_router(router)

# Fuzzer router
for router in gett_fuzzer_routers():
    app.include_router(router)

# Register WebSocket handlers
crawler_websocket_handlers = get_crawler_websocket_handlers()
dbf_websocket_handlers = get_dbf_websocket_handlers()
ml_websocket_handlers = get_ml_websocket_handlers()
fuzzer_websocket_handlers = get_fuzzer_websocket_handlers()

# WebSocket endpoint for crawler updates
@app.websocket('/ws/crawler/{job_id}')
async def crawler_socket(websocket: WebSocket, job_id: str):
    await crawler_websocket_handlers["crawler"](websocket, job_id)

@app.websocket('/ws/dbf/{job_id}')
async def dbf_socket(websocket: WebSocket, job_id: str):
    await dbf_websocket_handlers['dbf'](websocket, job_id)

@app.websocket('/ws/ml/{job_id}')
async def ml_socket(websocket: WebSocket, job_id: str):
    await ml_websocket_handlers['ml'](websocket, job_id)

@app.websocket('/ws/fuzzer/{job_id}')
async def fuzzer_socket(websocket: WebSocket, job_id: str):
    await fuzzer_websocket_handlers['fuzzer'](websocket, job_id)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "TRACE API is running."}

# For debugging - print raw request body
@app.post("/api/debug")
async def debug_endpoint(request: Request):
    body = await request.body()
    logger.info(f"Raw request body: {body}")
    try:
        json_body = await request.json()
        logger.info(f"JSON body: {json_body}")
        return {"received": json_body}
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return {"error": str(e), "raw_body": body.decode()}

# Changed to 0.0.0.0 to listen on all incoming connections.
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)