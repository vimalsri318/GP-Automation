"""FastAPI Main App"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import step1, step2, step3, step4, step5, step6, categories
from config import FRONTEND_URL, DEBUG

app = FastAPI(title="Revenue POC")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(step1.router)
app.include_router(step2.router)
app.include_router(step3.router)
app.include_router(step4.router)
app.include_router(step5.router)
app.include_router(step6.router)
app.include_router(categories.router)

@app.get("/health")
async def health():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG)
