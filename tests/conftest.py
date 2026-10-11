"""Utilidades compartidas: abrir el .docx generado para comprobar su contenido."""

import io

from docx import Document
from docx.text.paragraph import Paragraph


def open_docx(content: bytes):
    return Document(io.BytesIO(content))


def body(content: bytes) -> list[Paragraph]:
    """Párrafos del documento sin el título (el primero)."""
    return open_docx(content).paragraphs[1:]


def styles_and_texts(content: bytes) -> list[tuple[str, str]]:
    return [(p.style.name, p.text) for p in body(content)]
