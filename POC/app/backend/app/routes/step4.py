from fastapi import APIRouter
from app.services.step4_service import resolve_invoice_narration

router = APIRouter(prefix="/api/step4", tags=["Master Sync"])

@router.get("/validate/master_sync")
async def execute_step4():
    """Execute Step 4: Invoice & Narration Sync"""
    result = resolve_invoice_narration()
    # Relay the results directly from the service
    return result
