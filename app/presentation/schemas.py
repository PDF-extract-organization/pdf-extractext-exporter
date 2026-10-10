from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ExportRequest(BaseModel):
    title: NonBlankText
    markdown: str
    filename: str | None = Field(default=None, max_length=200)


class HealthResponse(BaseModel):
    status: str
    service: str
