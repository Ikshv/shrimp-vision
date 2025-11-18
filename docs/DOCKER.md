# Docker Setup Guide

This guide explains how to run Shrimp Vision using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d --build
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

## Services

- **Backend**: FastAPI server running on port `3100`
- **Frontend**: Next.js application running on port `3099`

Access the application at:
- Frontend: http://localhost:3099
- Backend API: http://localhost:3100
- API Docs: http://localhost:3100/docs

## Data Persistence

The following directories are mounted as volumes to persist data:
- `backend/static/` - Uploaded images and annotations
- `backend/models/` - Trained model files
- `backend/dataset/` - Training datasets
- `backend/exports/` - Exported datasets

## Development vs Production

### Development Mode
For development with hot-reload, you can still use the original `start.sh` script.

### Production Mode
Docker runs in production mode with:
- No hot-reload (optimized performance)
- Standalone Next.js build
- Health checks enabled
- Automatic restarts on failure

## Building Individual Services

```bash
# Build backend only
docker-compose build backend

# Build frontend only
docker-compose build frontend
```

## Environment Variables

You can customize the setup by creating a `.env` file in the root directory:

```env
# Backend
ENVIRONMENT=production
PYTHONUNBUFFERED=1

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3100
```

## Troubleshooting

### Port Already in Use
If ports 3099 or 3100 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3099:3099"  # Change first number to available port
```

### Permission Issues
If you encounter permission issues with mounted volumes:
```bash
# On Linux/Mac
sudo chown -R $USER:$USER backend/static backend/models backend/dataset backend/exports
```

### Rebuild After Code Changes
After making code changes, rebuild the images:
```bash
docker-compose up --build
```

### Clean Up
Remove all containers, networks, and volumes:
```bash
docker-compose down -v
```

## Production Deployment

For production deployment, consider:
1. Using environment-specific `.env` files
2. Setting up reverse proxy (nginx/traefik)
3. Using Docker secrets for sensitive data
4. Setting resource limits in `docker-compose.yml`
5. Using named volumes instead of bind mounts for better performance

Example production `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  backend:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

