from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class NewsCreate(BaseModel):
    title: str
    content: str
    meta_info: Optional[Dict[str, Any]] = None

class NewsResponse(NewsCreate):
    id: int
    model_config = {"from_attributes": True}

class VectorQueryRequest(BaseModel):
    query: str
    k: int = 5

class ChatRequest(BaseModel):
    session_id: str
    query: str
