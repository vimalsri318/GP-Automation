from fastapi import APIRouter
from app.services.step5_service import resolve_secondary_narration

router = APIRouter(
    prefix="/api/step5",
    tags=["step5"]
)

@router.get("/validate/secondary_narration")
async def secondary_narration_api():
    return resolve_secondary_narration()
