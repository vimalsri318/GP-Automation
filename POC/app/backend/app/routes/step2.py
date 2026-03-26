"""Step 2 Routes"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.step2_service import get_system_files, parse_zrecon, parse_revenue, parse_cost, cross_invoice_integrity, validate_eager_all

router = APIRouter(prefix="/api/step2", tags=["Step2"])

@router.get("/files")
async def list_files():
    """Returns the list of the 5 system files dynamically"""
    files = get_system_files()
    return {"success": True, "files": files}

@router.get("/validate/eager_all")
async def validate_eager_all_route():
    """New high-speed entry point for one-time parallel warmup"""
    return JSONResponse(status_code=200, content=validate_eager_all())

@router.get("/validate/zrecon")
async def validate_zrecon_route():
    return JSONResponse(status_code=200, content=parse_zrecon())

@router.get("/validate/revenue")
async def validate_revenue_route():
    return JSONResponse(status_code=200, content=parse_revenue())

@router.get("/validate/cost")
async def validate_cost_route():
    return JSONResponse(status_code=200, content=parse_cost())

@router.get("/validate/cross_invoice")
async def validate_cross_invoice_route():
    return JSONResponse(status_code=200, content=cross_invoice_integrity())
