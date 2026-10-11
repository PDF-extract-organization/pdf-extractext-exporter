"""Tests del exportador: se genera el .docx y se abre de nuevo con python-docx.

Se comprueban estilos y textos de los párrafos, no bytes.
"""

import pytest

from app.infrastructure.docx_exporter import DocxExporter
from tests.conftest import body, open_docx, styles_and_texts


@pytest.fixture
def exporter() -> DocxExporter:
    return DocxExporter()


def export(exporter, markdown: str, title: str = "Resumen: doc.pdf") -> bytes:
    return exporter.export(title, markdown)


def test_el_resultado_es_un_docx(exporter):
    assert export(exporter, "Hola").startswith(b"PK")  # un .docx es un zip


def test_el_titulo_es_el_primer_parrafo_con_estilo_heading_1(exporter):
    first = open_docx(export(exporter, "Hola", title="Resumen: informe.pdf")).paragraphs[0]

    assert first.style.name == "Heading 1"
    assert first.text == "Resumen: informe.pdf"


def test_un_markdown_vacio_deja_solo_el_titulo(exporter):
    assert body(export(exporter, "")) == []


def test_los_parrafos_se_conservan(exporter):
    content = export(exporter, "Primer párrafo.\n\nSegundo párrafo.")

    assert styles_and_texts(content) == [
        ("Normal", "Primer párrafo."),
        ("Normal", "Segundo párrafo."),
    ]


def test_un_salto_de_linea_simple_no_parte_el_parrafo(exporter):
    assert styles_and_texts(export(exporter, "una línea\notra línea")) == [
        ("Normal", "una línea otra línea")
    ]


@pytest.mark.parametrize(
    "markdown, style",
    [("# Título", "Heading 2"), ("## Sección", "Heading 3"), ("### Apartado", "Heading 4")],
)
def test_los_titulos_bajan_un_nivel_bajo_el_titulo_del_documento(exporter, markdown, style):
    (paragraph,) = body(export(exporter, markdown))

    assert paragraph.style.name == style
    assert paragraph.text == markdown.lstrip("# ")


def test_las_vinetas_usan_list_bullet(exporter):
    assert styles_and_texts(export(exporter, "- uno\n- dos\n* tres")) == [
        ("List Bullet", "uno"),
        ("List Bullet", "dos"),
        ("List Bullet", "tres"),
    ]


def test_las_listas_numeradas_usan_list_number(exporter):
    assert styles_and_texts(export(exporter, "1. uno\n2. dos")) == [
        ("List Number", "uno"),
        ("List Number", "dos"),
    ]


def test_las_listas_anidadas_usan_el_estilo_de_segundo_nivel(exporter):
    assert styles_and_texts(export(exporter, "- padre\n  - hijo")) == [
        ("List Bullet", "padre"),
        ("List Bullet 2", "hijo"),
    ]


def test_la_negrita_y_la_cursiva_se_aplican_a_sus_fragmentos(exporter):
    (paragraph,) = body(export(exporter, "texto **negrita** y *cursiva*"))

    runs = {run.text: run for run in paragraph.runs}
    assert paragraph.text == "texto negrita y cursiva"
    assert runs["negrita"].bold is True
    assert runs["cursiva"].italic is True
    assert not runs["texto "].bold


def test_la_negrita_dentro_de_una_vineta(exporter):
    (paragraph,) = body(export(exporter, "- un **punto** clave"))

    assert paragraph.style.name == "List Bullet"
    assert any(run.bold and run.text == "punto" for run in paragraph.runs)


def test_el_codigo_en_linea_usa_fuente_monoespaciada(exporter):
    (paragraph,) = body(export(exporter, "usa `pytest` siempre"))

    code = next(run for run in paragraph.runs if run.text == "pytest")
    assert code.font.name == "Consolas"


def test_un_bloque_de_codigo_se_conserva_en_monoespaciada(exporter):
    (paragraph,) = body(export(exporter, "```\nprint('hola')\n```"))

    assert paragraph.text == "print('hola')"
    assert all(run.font.name == "Consolas" for run in paragraph.runs)


def test_un_enlace_conserva_su_texto(exporter):
    assert styles_and_texts(export(exporter, "ver [la web](https://x.test)")) == [
        ("Normal", "ver la web")
    ]


def test_un_resumen_completo_con_titulos_vinetas_y_negritas(exporter):
    markdown = (
        "# Resumen\n\n"
        "El documento trata de **tres** temas:\n\n"
        "- Primero\n"
        "- Segundo\n\n"
        "## Conclusión\n\n"
        "Fin."
    )

    assert styles_and_texts(export(exporter, markdown)) == [
        ("Heading 2", "Resumen"),
        ("Normal", "El documento trata de tres temas:"),
        ("List Bullet", "Primero"),
        ("List Bullet", "Segundo"),
        ("Heading 3", "Conclusión"),
        ("Normal", "Fin."),
    ]
