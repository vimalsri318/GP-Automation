from fastapi import APIRouter, Body
from app.services.category_master_service import get_category_mappings, save_category_mappings
from typing import List, Dict

router = APIRouter(
    prefix="/api/categories",
    tags=["categories"]
)

@router.get("/")
async def get_categories_api():
    return {"success": True, "mappings": get_category_mappings()}

@router.post("/")
async def update_categories_api(data: List[Dict[str, str]] = Body(...)):
    try:
        success = save_category_mappings(data)
        return {"success": success, "message": "Master categories updated successfully."}
    except Exception as e:
        return {"success": False, "error": str(e)}
