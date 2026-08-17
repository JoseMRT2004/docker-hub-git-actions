# DevOps Landing Page

Landing page personal de Jose M. Taveras — DevOps Engineer.

## Deploy automático

Cada push a `main` ejecuta:

1. Build y push de imagen Docker a Docker Hub
2. Deploy automático a Render (Static Site)

## Secrets necesarios en GitHub

| Secret | Descripción |
|--------|-------------|
| `DOCKER_USERNAME` | Usuario de Docker Hub |
| `DOCKER_PASSWORD` | Token de Docker Hub |
| `RENDER_API_KEY` | API key de Render |
| `RENDER_SERVICE_ID` | ID del servicio en Render |

## Correr local

```bash
docker build -t devops-landing .
docker run -p 8080:80 devops-landing
```

Abrí http://localhost:8080
