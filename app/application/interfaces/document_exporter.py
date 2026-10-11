"""Puerto de exportación: el router no sabe cómo se construye el documento."""

from abc import ABC, abstractmethod


class DocumentExporter(ABC):
    @abstractmethod
    def export(self, title: str, markdown: str) -> bytes:
        """Devuelve el documento con el título y el contenido en Markdown."""
