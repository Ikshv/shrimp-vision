# Deployment Checklist

## ✅ Pre-Deployment Verification

Before pulling this repository on another PC and building Docker containers, verify:

### Required Files
- [x] `docker-compose.yml` - Docker orchestration
- [x] `backend/Dockerfile` - Backend container definition
- [x] `frontend/Dockerfile` - Frontend container definition
- [x] `backend/requirements.txt` - Python dependencies
- [x] `frontend/package.json` - Node.js dependencies
- [x] `.dockerignore` files in both backend and frontend

### Prerequisites on Target Machine
- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Ports 3099 and 3100 available
- [ ] At least 4GB free disk space
- [ ] Git installed (for cloning)

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd shrimp-vision
```

### 2. Build and Start
```bash
docker-compose up --build
```

### 3. Verify Services
- Frontend: http://localhost:3099
- Backend: http://localhost:3100
- API Docs: http://localhost:3100/docs

## ⚠️ Important Notes

1. **Data Persistence**: Data directories are mounted as volumes:
   - `backend/static/` - Uploads and annotations
   - `backend/models/` - Trained models
   - `backend/dataset/` - Training datasets
   - `backend/exports/` - Exported files

2. **First Run**: The first build will take longer (5-10 minutes) as it downloads base images and installs dependencies.

3. **Port Conflicts**: If ports 3099 or 3100 are in use, modify `docker-compose.yml`:
   ```yaml
   ports:
     - "YOUR_PORT:3100"  # Change first number
   ```

4. **Platform Compatibility**: Docker setup works on:
   - Linux (x86_64, ARM64)
   - macOS (Intel, Apple Silicon)
   - Windows (with WSL2 or Docker Desktop)

## 🔍 Troubleshooting

### Build Fails
- Check Docker and Docker Compose versions
- Ensure sufficient disk space
- Check internet connection (needs to download base images)

### Containers Won't Start
- Check port availability: `docker ps`
- View logs: `docker-compose logs`
- Check volume permissions (Linux)

### Performance Issues
- Allocate more resources to Docker
- Use named volumes instead of bind mounts for better performance

## 📝 Post-Deployment

After successful deployment:
1. Test image upload
2. Test annotation tool
3. Test model training
4. Verify data persistence (restart containers, data should remain)

