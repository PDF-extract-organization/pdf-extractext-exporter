"""Tests de los endpoints HTTP. Sin red ni servicios externos."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import open_docx

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def exportar(client, **campos):
    payload = {"title": "Resumen: doc.pdf", "markdown": "# Hola\n\n- uno"} | campos
    return client.post("/docx", json=payload)


def test_docx_devuelve_un_documento_word(client):
    response = exportar(client)

    assert response.status_code == 200
    assert response.headers["content-type"] == DOCX_MIME
    assert response.content.startswith(b"PK")


def test_docx_contiene_el_titulo_y_el_markdown(client):
    document = open_docx(exportar(client).content)

    assert [p.text for p in document.paragraphs] == ["Resumen: doc.pdf", "Hola", "uno"]


def test_docx_propone_un_nombre_por_defecto(client):
    disposition = exportar(client).headers["content-disposition"]

    assert disposition == 'attachment; filename="resumen.docx"'


def test_docx_usa_el_nombre_pedido(client):
    disposition = exportar(client, filename="resumen_informe.docx").headers[
        "content-disposition"
    ]

    assert disposition == 'attachment; filename="resumen_informe.docx"'


def test_docx_anade_la_extension_si_falta(client):
    disposition = exportar(client, filename="informe").headers["content-disposition"]

    assert disposition == 'attachment; filename="informe.docx"'


@pytest.mark.parametrize(
    "pedido",
    ['../../etc/passwd', 'a"b\r\nX-Inyectada: 1', "carpeta\\archivo"],
)
def test_docx_sanea_el_nombre_del_archivo(client, pedido):
    response = exportar(client, filename=pedido)

    disposition = response.headers["content-disposition"]
    filename = disposition.removeprefix('attachment; filename="').removesuffix('"')
    assert response.status_code == 200
    assert "x-inyectada" not in response.headers
    assert not set(filename) & set('/\\"\r\n')
    assert filename.endswith(".docx")


@pytest.mark.parametrize("campos", [{"title": None}, {"markdown": None}])
def test_docx_sin_titulo_o_markdown_devuelve_422(client, campos):
    payload = {"title": "t", "markdown": "m"} | campos
    payload = {k: v for k, v in payload.items() if v is not None}

    assert client.post("/docx", json=payload).status_code == 422


def test_health_responde_healthy(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "exporter"}
