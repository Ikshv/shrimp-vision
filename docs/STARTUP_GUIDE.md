# Shrimp Vision - Quick Start Guide

## Starting the Application

### 1. Start Backend (Terminal 1)
```bash
cd backend
python run.py
# or
uvicorn main:app --host 0.0.0.0 --port 3100 --reload
```
**Backend will run on**: http://localhost:3100

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
**Frontend will run on**: http://localhost:3099

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:3099 | Main application interface |
| **Backend API** | http://localhost:3100 | FastAPI backend |
| **API Docs** | http://localhost:3100/docs | Swagger/OpenAPI documentation |
| **Static Files** | http://localhost:3099/static/* | Images (proxied through Next.js) |

## Application Flow

### 1. Upload Images
- Navigate to http://localhost:3099/upload
- Drag & drop or select images
- Supported formats: JPG, PNG, BMP, TIFF, HEIC, HEIF, WEBP, GIF

### 2. Annotate Shrimp
- Navigate to http://localhost:3099/annotate
- Select a class from the class selector buttons
- Click and drag to draw bounding boxes around shrimp
- Save annotations for each image

### 3. Train Model
- Navigate to http://localhost:3099/train
- Configure training parameters (epochs, batch size, model size)
- Start training
- Monitor progress in real-time

### 4. Test/Inference
- Navigate to http://localhost:3099/test
- Upload a new image
- Select trained model
- Adjust confidence threshold
- View detection results

### 5. View Gallery
- Navigate to http://localhost:3099/gallery
- Browse all uploaded images
- Delete or annotate images

## Multi-Class Annotation

The system now supports 6 different shrimp classes:

| Class | Color | Description |
|-------|-------|-------------|
| 🦐 **Shrimp** | Green | Regular shrimp |
| 🐣 **Juvenile** | Blue | Young/small shrimp |
| 🦐 **Adult** | Purple | Mature shrimp |
| 🥚 **Egg** | Amber | Shrimp eggs |
| 👻 **Molt** | Gray | Molted shells |
| 💀 **Dead** | Red | Dead shrimp |

### How to Use Multi-Tagging:
1. In the annotation page, select the class from the button group above the image
2. Draw bounding boxes - they will automatically be tagged with the selected class
3. Each class displays with its own color for easy identification
4. View class statistics in the sidebar

## Project Structure

```
shrimp-vision/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── run.py               # Backend startup script
│   ├── config/
│   │   └── classes.py       # Multi-class configuration
│   ├── routes/              # API endpoints
│   │   ├── upload.py
│   │   ├── annotate.py
│   │   ├── train.py
│   │   ├── inference.py
│   │   └── export.py
│   ├── services/            # Business logic
│   └── static/
│       ├── uploads/         # Uploaded images
│       └── annotations/     # Annotation JSON files
│
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── page.tsx         # Home
│   │   ├── upload/          # Upload page
│   │   ├── annotate/        # Annotation tool
│   │   ├── train/           # Training interface
│   │   ├── test/            # Inference page
│   │   └── gallery/         # Image gallery
│   ├── lib/
│   │   └── config.ts        # Image URL configuration
│   └── next.config.js       # Next.js configuration
```

## Troubleshooting

### Images Not Loading
1. Check backend is running on port 3100
2. Check frontend is running on port 3099  
3. Verify `next.config.js` has static file proxy
4. Check browser console for errors
5. Verify images exist in `backend/static/uploads/`

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 3099
lsof -ti:3099 | xargs kill -9

# Kill process on port 3100
lsof -ti:3100 | xargs kill -9
```

### Backend Not Starting
```bash
# Ensure Python dependencies are installed
cd backend
pip install -r requirements.txt

# Check if directories exist
mkdir -p static/uploads static/annotations models
```

### Frontend Not Starting
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
```

## Development Tips

### Hot Reload
- Backend: Uses `--reload` flag with uvicorn
- Frontend: Next.js automatically hot reloads

### API Testing
- Use Swagger UI: http://localhost:3100/docs
- Or use curl/Postman to test endpoints

### Viewing Logs
- **Backend**: Logs appear in Terminal 1
- **Frontend**: Logs appear in Terminal 2 and browser console

### Adding New Classes
Edit `backend/config/classes.py`:
```python
AVAILABLE_CLASSES = {
    "new_class": {
        "id": 6,
        "name": "new_class",
        "display_name": "New Class",
        "color": "#FF5733",
        "description": "Description here"
    }
}
```

## Environment Variables (Optional)

Create `.env.local` in frontend directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:3100
```

## Quick Command Reference

```bash
# Start everything
./start.sh  # Main startup script (in root)
# Or use utility scripts from scripts/ directory
./scripts/restart.sh  # Restart application
./scripts/setup.sh    # Initial setup

# Backend only
cd backend && python run.py

# Frontend only  
cd frontend && npm run dev

# Build frontend
cd frontend && npm run build

# Run frontend production
cd frontend && npm start

# Check what's running
lsof -i:3099  # Frontend
lsof -i:3100  # Backend

# Test API
curl http://localhost:3100/api/health

# Test image loading
curl http://localhost:3099/static/uploads/[filename]
```





