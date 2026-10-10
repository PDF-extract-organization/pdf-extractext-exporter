import re

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool

from app.application.interfaces.document_exporter import DocumentExporter
from app.dependencies import get_exporter
from app.presentation.schemas import ExportRequest, HealthResponse

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DEFAULT_FILENAME = "resumen.docx"

router = APIRouter()


def safe_filename(requested: str | None) -> str:
    """Nombre apto para la cabecera Content-Disposition.

    Solo letras, números, guiones, guiones bajos y puntos ASCII: así no caben
    rutas, comillas ni saltos de línea que inyecten cabeceras.
    """
    if not requested:
        return DEFAULT_FILENAME
    name = re.sub(r"[^\w\-.]", "_", requested, flags=re.ASCII).lstrip(".")
    if not name:
        return DEFAULT_FILENAME
    return name if name.lower().endswith(".docx") else f"{name}.docx"


@router.post("/docx")
async def export_docx(
    request: ExportRequest,
    exporter: DocumentExporter = Depends(get_exporter),
):
    content = await run_in_threadpool(exporter.export, request.title, request.markdown)
    return Response(
        content=content,
        media_type=DOCX_MIME,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename(request.filename)}"'
        },
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", service="exporter")
