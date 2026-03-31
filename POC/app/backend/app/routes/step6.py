from fastapi import APIRouter
from app.services.step6_service import execute_step6_category_mapping

router = APIRouter(
    prefix="/api/step6",
    tags=["step6"]
)

@router.get("/process")
async def step6_process_api():
    return execute_step6_category_mapping()
