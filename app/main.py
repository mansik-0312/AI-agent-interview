from fastapi import FastAPI
from beanie import init_beanie
from app.database import db
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_beanie(database=db)
    yield
    
app = FastAPI(lifespan=lifespan)



