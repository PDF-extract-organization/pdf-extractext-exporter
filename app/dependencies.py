"""Cableado de dependencias. Router y main lo importan; él no importa a ninguno."""

from functools import lru_cache

from app.application.interfaces.document_exporter import DocumentExporter
from app.infrastructure.docx_exporter import DocxExporter


@lru_cache
def get_exporter() -> DocumentExporter:
    return DocxExporter()
