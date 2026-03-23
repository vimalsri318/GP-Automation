"""Step 1 Routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.services.step1_service import process_files

router = APIRouter(prefix="/api/step1", tags=["Step1"])


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process revenue files"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files")

        # Read files
        files_dict = {}
        for file in files:
            content = await file.read()
            files_dict[file.filename] = content

        # Process
        result = process_files(files_dict)

        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Processed {len(result['files'])} files",
                    "files": result["files"],
                    "execution_time_ms": result["execution_time_ms"]
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "errors": result["errors"],
                    "execution_time_ms": result["execution_time_ms"]
                }
            )

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
