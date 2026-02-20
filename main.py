from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import json
import database, schema, vector_store, rag

app = FastAPI(title="RAG News API", description="Full-featured API for RDBMS CRUD and Vector similarity search + LLM generation.")

@app.on_event("startup")
def on_startup():
    # Attempt to enable pgvector extension (requires pg superuser)
    try:
        with database.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    except Exception as e:
        print(f"Warning: Could not create pgvector extension automatically. Ensure it is enabled. Error: {e}")
        
    database.Base.metadata.create_all(bind=database.engine)

@app.post("/db/news", response_model=schema.NewsResponse)
def create_news(news: schema.NewsCreate, db: Session = Depends(database.get_db)):
    db_news = database.News(**news.model_dump())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@app.get("/db/news/{news_id}", response_model=schema.NewsResponse)
def get_news(news_id: int, db: Session = Depends(database.get_db)):
    db_news = db.query(database.News).filter(database.News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news

@app.post("/db/news/bulk", response_model=List[schema.NewsResponse])
async def create_news_bulk(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    content = await file.read()
    try:
        data = json.loads(content)
        news_items = [database.News(**item) for item in data]
        db.add_all(news_items)
        db.commit()
        for item in news_items:
            db.refresh(item)
        return news_items
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {str(e)}")

@app.post("/vector/ingest")
def vector_ingest(news: schema.NewsCreate):
    ids = vector_store.add_to_vector_store(texts=[news.content], metadatas=[{"title": news.title, **(news.meta_info or {})}])
    return {"message": "News ingested into vector DB", "inserted_ids": ids}

@app.post("/vector/ingest/bulk")
async def vector_ingest_bulk(file: UploadFile = File(...)):
    content = await file.read()
    try:
        data = json.loads(content)
        texts = [item["content"] for item in data]
        metadatas = [{"title": item["title"], **item.get("meta_info", {})} for item in data]
        ids = vector_store.add_to_vector_store(texts=texts, metadatas=metadatas)
        return {"message": f"{len(ids)} items ingested into vector DB"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {str(e)}")

@app.post("/rag/retrieve")
def rag_retrieve(request: schema.VectorQueryRequest):
    docs = vector_store.search_vector_store(request.query, k=request.k)
    return {"results": [{"content": d.page_content, "metadata": d.metadata} for d in docs]}

@app.post("/rag/generate")
def rag_generate(request: schema.VectorQueryRequest):
    summary = rag.generate_summary(request.query, k=request.k)
    return {"summary": summary}

@app.post("/rag/chat")
def rag_chat(request: schema.ChatRequest):
    response = rag.chat_with_history(request)
    return {"response": response}
