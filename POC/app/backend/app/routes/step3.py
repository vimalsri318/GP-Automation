from fastapi import APIRouter
from app.services.step3_service import resolve_cmir_types

router = APIRouter(prefix="/api/step3", tags=["Step 3"])

@router.get("/validate/cmir_resolution")
async def validate_cmir():
    """Triggers the Step 3 CMIR Resolution Flow."""
    try:
        return resolve_cmir_types()
    except Exception as e:
        return {"success": False, "error": str(e)}
