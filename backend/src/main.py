from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.database import connect_db, close_db
from src.app.auth import router as auth_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Admin API",
    description="Admin authentication API with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Admin API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}