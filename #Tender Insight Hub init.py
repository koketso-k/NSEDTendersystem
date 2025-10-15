from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# Import submodule routes
from . import search, summarization, scoring

__all__ = ["router"]