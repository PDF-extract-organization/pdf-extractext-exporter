# pdf-extractext-exporter

Microservicio que convierte un resumen en Markdown en un documento Word (`.docx`).
Forma parte de [pdf-extractext](https://github.com/PDF-extract-organization/pdf-extractext),
dividido en microservicios (épica: pdf-extractext#64).

Es *stateless*: no accede a la base de datos. Quien lo llama le pasa el título y el
contenido.

## Contrato HTTP

Escucha en el puerto `8000`. En el stack completo, Traefik le quita el prefijo
`/exporter`, así que desde fuera las rutas son `http://pdf.localhost/exporter/...`.

| Método y ruta | Entrada | Respuesta |
|---|---|---|
| `POST /docx` | JSON `{"title", "markdown", "filename"?}` | `200` con el `.docx` |
| `GET /health` | — | `200` `{"status": "healthy", "service": "exporter"}` |

La respuesta de `/docx` lleva `Content-Type:
application/vnd.openxmlformats-officedocument.wordprocessingml.document` y
`Content-Disposition: attachment; filename="..."`.

- `title` es obligatorio y no puede estar en blanco. `markdown` es obligatorio, pero
  puede estar vacío.
- `filename` es opcional (por defecto `resumen.docx`). Se sanea: solo quedan letras,
  números, `-`, `_` y `.` ASCII, y se añade `.docx` si falta. Así no caben rutas,
  comillas ni saltos de línea que inyecten cabeceras.

Errores: `422` si falta `title` o `markdown`, o si `filename` supera 200 caracteres.

## Markdown soportado

El Markdown se interpreta con [markdown-it-py](https://github.com/executablebooks/markdown-it-py)
(CommonMark), y el documento se construye recorriendo sus tokens. Hay un único parser,
sin expresiones regulares a mano.

| Markdown | En Word |
|---|---|
| Título del documento (`title`) | `Heading 1`, en azul |
| `#`, `##`, `###`… | `Heading 2`, `Heading 3`, `Heading 4`…: un nivel por debajo del título |
| Párrafos | `Normal`. Un salto de línea simple no parte el párrafo |
| `-` / `*` | `List Bullet`; anidadas, `List Bullet 2` y `3` |
| `1.` | `List Number`; anidadas, `List Number 2` y `3` |
| `**negrita**`, `*cursiva*` | Negrita y cursiva en su fragmento |
| `` `código` `` y bloques de código | Fuente `Consolas` |
| Enlaces | Se conserva el texto |

No soporta tablas, imágenes ni HTML: su texto se pierde o queda como párrafo normal.
Las listas numeradas de Word continúan la numeración entre listas separadas.

## Desarrollo

```bash
uv sync --group dev
uv run pytest                      # abre el .docx generado y comprueba estilos y textos
uv run uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t pdf-extractext-exporter .
docker run -p 8000:8000 pdf-extractext-exporter

curl -H "Content-Type: application/json" \
  -d '{"title": "Resumen: doc.pdf", "markdown": "# Hola\n\n- uno", "filename": "resumen_doc"}' \
  http://localhost:8000/docx --output resumen_doc.docx
```

En Windows, si el texto lleva acentos, envíalo desde un archivo en UTF-8
(`--data-binary @cuerpo.json`).

La imagen corre con un usuario sin privilegios y declara un `HEALTHCHECK`. Al integrar
en `main`, la CI la publica en `ghcr.io/pdf-extract-organization/pdf-extractext-exporter`.

## Arquitectura

| Capa | Contiene |
|---|---|
| `app/application/interfaces` | Puerto `DocumentExporter` |
| `app/infrastructure` | `DocxExporter`: el único sitio que importa `python-docx` y `markdown-it-py` |
| `app/presentation` | Router (valida, delega y responde) y schemas |
| `app/dependencies.py` | Cableado; lo importan el router y `main` |

## Flujo de trabajo

`main` y `develop` son las ramas principales. Los cambios entran por pull request a
`develop`, con los tests en verde en la CI. Los commits citan el issue (`#1`).
