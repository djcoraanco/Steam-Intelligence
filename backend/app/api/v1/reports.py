import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.export_service import ExportService, EXPORTS_DIR
from app.services.ai_analyst import AIAnalystService

router = APIRouter(prefix="/reports", tags=["reports"])


class ExportRequest(BaseModel):
    report_type: str = "market_summary"
    format: str = "pdf"  # json, csv, xlsx, pdf, pptx
    genre: Optional[str] = "Action"
    custom_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


@router.post("/export")
async def create_report_export(
    payload: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Asynchronously or synchronously generates a publication-grade report in PDF, PPTX, XLSX, CSV, or JSON.
    """
    ai_service = AIAnalystService(db)
    analysis = await ai_service.analyze_market_question(
        question=f"Executive analysis for segment {payload.genre}",
        target_genre=payload.genre
    )

    if payload.custom_title:
        analysis["title"] = payload.custom_title

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    clean_genre = re.sub(r"[^a-zA-Z0-9_-]", "", payload.genre or "market")
    base_filename = f"steam_intelligence_{clean_genre}_{timestamp}"

    fmt = payload.format.lower()
    if fmt == "json":
        filename = f"{base_filename}.json"
        filepath = ExportService.generate_json_export(analysis, filename)
    elif fmt == "csv":
        filename = f"{base_filename}.csv"
        rows = [
            {"claim": f.get("claim"), "metric": f.get("metric"), "confidence": f.get("confidence")}
            for f in analysis.get("findings", [])
        ] or [{"status": "no_findings"}]
        filepath = ExportService.generate_csv_export(rows, filename)
    elif fmt == "xlsx":
        filename = f"{base_filename}.xlsx"
        sheets_data = {
            "Executive Summary": [{"title": analysis["title"], "summary": analysis["summary"]}],
            "Findings": [
                {"claim": f.get("claim"), "metric": f.get("metric"), "confidence": f.get("confidence")}
                for f in analysis.get("findings", [])
            ],
            "Recommendations": [{"recommendation": r} for r in analysis.get("recommendations", [])],
            "Limitations": [{"limitation": l} for l in analysis.get("limitations", [])]
        }
        filepath = ExportService.generate_xlsx_export(sheets_data, filename)
    elif fmt == "pptx":
        filename = f"{base_filename}.pptx"
        filepath = ExportService.generate_pptx_export(analysis, filename)
    elif fmt == "pdf":
        filename = f"{base_filename}.pdf"
        filepath = ExportService.generate_pdf_export(analysis, filename)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}. Supported: json, csv, xlsx, pdf, pptx")

    return {
        "status": "ready",
        "format": fmt,
        "filename": filename,
        "download_url": f"/api/v1/reports/download/{filename}",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/download/{filename}")
def download_report(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Secure file download endpoint with directory traversal protection.
    """
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(EXPORTS_DIR, safe_filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Export file not found")

    ext = os.path.splitext(safe_filename)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".csv": "text/csv",
        ".json": "application/json"
    }

    return FileResponse(
        path=filepath,
        filename=safe_filename,
        media_type=media_types.get(ext, "application/octet-stream")
    )
