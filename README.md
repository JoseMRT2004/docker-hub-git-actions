# DevOps Landing Page

Landing page personal de Jose M. Taveras — Software Dev. | DevOps.

## Deploy automático

Cada push a `main` ejecuta:

1. Instala dependencias y corre las pruebas unitarias (`uv run pytest`)
2. Build y push de imagen Docker a Docker Hub (solo si los tests pasan)
3. Deploy automático a Render

## Secrets necesarios en GitHub

| Secret | Descripción |
|--------|-------------|
| `DOCKER_USERNAME` | Usuario de Docker Hub |
| `DOCKER_PASSWORD` | Token de Docker Hub |
| `RENDER_API_KEY` | API key de Render |
| `RENDER_SERVICE_ID` | ID del servicio en Render |

## Pruebas unitarias

Los tests validan el contenido del landing (hero, experiencia, assets)
y que el pipeline tenga el orden correcto:

```bash
uv sync --dev
uv run pytest
```

## Correr local

```bash
docker build -t devops-landing .
docker run -p 8080:80 devops-landing
```

Abrí http://localhost:8080
