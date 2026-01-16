from fastapi import FastAPI, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud import *
from database.session import get_db_session
from services.tmdb_api import search_content, get_movie_details

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)