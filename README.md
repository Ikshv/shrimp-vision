# 🦐 Shrimp Vision - AI Shrimp Detection System

A complete full-stack application for shrimp detection and counting using computer vision. Upload aquarium images, annotate shrimp, train YOLOv8 models, and deploy for real-time detection.

![Shrimp Vision](https://img.shields.io/badge/Shrimp-Vision-orange?style=for-the-badge&logo=shrimp)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

## ✨ Features

### 🖼️ Image Management
- **Drag & Drop Upload**: Upload multiple aquarium images with support for JPG, PNG, WEBP, HEIC, BMP, TIFF
- **Image Gallery**: Browse and manage all uploaded images
- **Batch Processing**: Handle multiple images simultaneously
- **Image Validation**: Automatic format and size validation

### 🎯 Annotation Tool
- **Interactive Bounding Boxes**: Click and drag to draw precise bounding boxes around shrimp
- **Multi-class Support**: 6 different classes (Shrimp, Juvenile, Adult, Egg, Molt, Dead)
- **Color-coded Classes**: Visual distinction with unique colors per class
- **Real-time Feedback**: Visual feedback with labeled annotations
- **Navigation**: Easy previous/next navigation between images
- **Auto-save**: Automatic saving of annotation progress
- **Statistics**: Real-time count of annotated shrimp and progress tracking

### 🧠 Model Training
- **YOLOv8 Integration**: Support for all YOLOv8 model sizes (nano, small, medium, large, xlarge)
- **Live Training Progress**: Real-time monitoring of training metrics (loss, accuracy, epochs)
- **WebSocket Updates**: Real-time progress updates via WebSocket
- **Configurable Parameters**: Adjustable epochs, batch size, learning rate, image size
- **Dataset Splitting**: Automatic train/validation split (80/20 by default)
- **Early Stopping**: Built-in early stopping to prevent overfitting

### 🔍 Inference & Testing
- **Real-time Detection**: Test trained models on new images
- **Confidence Thresholding**: Adjustable confidence levels for detection
- **Visual Results**: Annotated images with bounding boxes and confidence scores
- **Batch Processing**: Test multiple images at once
- **Performance Metrics**: Processing time and accuracy statistics

### 📦 Export & Deployment
- **Model Export**: Download trained models in PyTorch format (.pt)
- **Dataset Export**: Export complete datasets in YOLO format
- **Annotation Export**: Export annotations in JSON or YOLO format
- **ZIP Archives**: Convenient packaging of all assets
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

```
shrimp-vision/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── run.py              # Server startup script
│   ├── routes/             # API route handlers
│   │   ├── upload.py       # Image upload endpoints
│   │   ├── annotate.py     # Annotation management
│   │   ├── train.py        # Model training endpoints
│   │   ├── inference.py    # Model inference endpoints
│   │   ├── export.py       # Data export endpoints
│   │   └── websocket.py    # WebSocket for real-time updates
│   ├── services/           # Core business logic
│   │   ├── dataset_manager.py    # Dataset preparation and management
│   │   ├── model_trainer.py      # YOLOv8 training pipeline
│   │   └── inference_engine.py   # Model inference engine
│   ├── config/             # Configuration files
│   │   └── classes.py      # Multi-class definitions
│   ├── static/             # Static files (uploads, annotations)
│   ├── models/             # Trained model storage
│   ├── dataset/            # Training datasets
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js 14+ app directory
│   │   ├── page.tsx       # Home page
│   │   ├── upload/        # Image upload page
│   │   ├── annotate/      # Annotation tool page
│   │   ├── train/         # Model training page
│   │   ├── test/          # Testing and inference page
│   │   └── gallery/       # Image gallery page
│   ├── components/        # React components
│   │   └── TrainingProgress.tsx
│   ├── lib/               # Utility functions
│   │   └── config.ts      # API configuration
│   └── package.json       # Node.js dependencies
├── scripts/                # Utility scripts
│   ├── start.bat          # Windows startup script
│   ├── restart.sh         # Restart application
│   ├── setup.sh           # Initial setup
│   └── README.md          # Scripts documentation
├── docs/                   # Additional documentation
│   ├── DOCKER.md          # Docker setup guide
│   ├── STARTUP_GUIDE.md   # Detailed startup instructions
│   └── ...                # Other guides
├── docker-compose.yml     # Docker orchestration
├── start.sh               # Main startup script (Linux/macOS)
├── README.md              # This file
└── QUICKSTART.md         # Quick start guide
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git** for cloning the repository
- **Docker** (optional, for containerized deployment)

### Installation

#### Option 1: Docker (Recommended)

```bash
git clone <repository-url>
cd shrimp-vision
docker-compose up --build
```

See [Docker Setup Guide](docs/DOCKER.md) for detailed instructions.

#### Option 2: Automated Script

**macOS/Linux:**
```bash
git clone <repository-url>
cd shrimp-vision
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
git clone <repository-url>
cd shrimp-vision
scripts\start.bat
```

#### Option 3: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shrimp-vision
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

#### Using Docker
```bash
docker-compose up
```

#### Using Startup Script
```bash
./start.sh  # macOS/Linux
scripts\start.bat  # Windows
```

#### Manual Start

1. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python run.py
   ```
   The API will be available at `http://localhost:3100`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The web application will be available at `http://localhost:3099`

3. **Open your browser**
   Navigate to `http://localhost:3099` to start using Shrimp Vision!

## 📖 Usage Guide

### 1. Upload Images
- Navigate to the **Upload** page
- Drag and drop aquarium images or click to select files
- Supported formats: JPG, PNG, WEBP, HEIC, BMP, TIFF
- Recommended: High-resolution images (640×640+ pixels) with good lighting

### 2. Annotate Shrimp
- Go to the **Annotate** page
- Select a class from the button group (Shrimp, Juvenile, Adult, Egg, Molt, Dead)
- Click and drag to draw bounding boxes around each shrimp
- Use the navigation buttons to move between images
- Save annotations regularly using the "Save" button
- Aim for at least 5-10 annotated images for initial training

### 3. Train Model
- Visit the **Train** page
- Select your preferred YOLOv8 model size:
  - **Nano (yolov8n)**: Fastest, smallest, good for real-time
  - **Small (yolov8s)**: Balanced speed and accuracy
  - **Medium (yolov8m)**: Good balance for most use cases
  - **Large (yolov8l)**: Higher accuracy, slower inference
  - **XLarge (yolov8x)**: Highest accuracy, slowest inference
- Adjust training parameters (epochs, batch size, learning rate)
- Click "Start Training" and monitor progress in real-time
- Training typically takes 10-60 minutes depending on dataset size

### 4. Test & Export
- Go to the **Test** page
- Select a trained model and upload a test image
- Adjust confidence threshold as needed
- View detection results with bounding boxes
- Export your trained model or complete dataset

## 🔧 Configuration

### Backend Configuration

The backend runs on port `3100` by default. Configuration can be modified in `backend/run.py`:

```python
# Server configuration
host = "0.0.0.0"  # Listen on all interfaces
port = 3100
```

### Frontend Configuration

Frontend configuration is handled through environment variables in `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:3100
```

The frontend runs on port `3099` by default (configured in `package.json`).

## 📊 API Documentation

When the backend is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:3100/docs
- **ReDoc**: http://localhost:3100/redoc

### Main Endpoints

**Upload**
- `POST /api/upload/` - Upload multiple images
- `GET /api/upload/list` - List uploaded images
- `DELETE /api/upload/{id}` - Delete an image

**Annotation**
- `POST /api/annotate/save` - Save annotation for an image
- `GET /api/annotate/{id}` - Get annotation for an image
- `GET /api/annotate/classes` - Get available classes
- `GET /api/annotate/stats/summary` - Get annotation statistics

**Training**
- `POST /api/train/start` - Start model training
- `GET /api/train/status` - Get training status
- `POST /api/train/stop` - Stop training

**Inference**
- `POST /api/inference/predict` - Run inference on an image
- `GET /api/inference/models/available` - List available models

**Export**
- `POST /api/export/dataset` - Export complete dataset
- `GET /api/export/model/{name}` - Download a specific model

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python run.py  # Development server with auto-reload
```

### Frontend Development

```bash
cd frontend
npm run dev     # Development server with hot reload
npm run build   # Production build
npm start       # Production server
```

### Code Structure

- **Backend**: FastAPI with async/await patterns, Pydantic models for validation
- **Frontend**: Next.js 14+ with App Router, TypeScript, Tailwind CSS
- **State Management**: React hooks with local state
- **API Communication**: Axios with interceptors for error handling
- **Real-time Updates**: WebSocket for training progress
- **UI Components**: Custom components with Tailwind CSS styling

## 🐳 Docker Deployment

Shrimp Vision is fully containerized and ready for deployment:

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

See [Docker Setup Guide](docs/DOCKER.md) for detailed instructions.

## 📈 Performance Tips

### For Better Training Results
1. **Dataset Quality**: Use high-quality, well-lit images
2. **Annotation Accuracy**: Ensure precise bounding boxes
3. **Dataset Size**: Aim for 50+ annotated images for good results
4. **Data Diversity**: Include various angles, lighting, and shrimp positions
5. **Model Selection**: Start with YOLOv8n for quick iteration, upgrade to larger models for production

### For Better Performance
1. **GPU Training**: Use CUDA-enabled GPU for faster training
2. **Batch Size**: Increase batch size if you have more GPU memory
3. **Image Size**: Use appropriate image size (640px is usually sufficient)
4. **Model Size**: Choose the right model size for your speed/accuracy requirements

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
- Ensure Python 3.11+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify port 3100 is not in use: `lsof -i:3100` (macOS/Linux) or `netstat -ano | findstr :3100` (Windows)

**Frontend won't start**
- Ensure Node.js 18+ is installed
- Install dependencies: `npm install`
- Check that port 3099 is not in use

**Training fails**
- Ensure you have at least 5 annotated images
- Check available disk space (need at least 2GB)
- Verify CUDA installation if using GPU

**Inference is slow**
- Try using a smaller model (yolov8n)
- Reduce image size in training configuration
- Use GPU for inference if available

**Docker issues**
- Ensure Docker and Docker Compose are installed
- Check ports 3099 and 3100 are not in use
- See [Docker Setup Guide](docs/DOCKER.md) for detailed troubleshooting

### Getting Help

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review the API documentation at `http://localhost:3100/docs`
3. Check browser console for frontend errors
4. Check backend logs for server errors
5. Review the [Startup Guide](docs/STARTUP_GUIDE.md) for common issues

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Docker Setup](docs/DOCKER.md)** - Containerized deployment
- **[Startup Guide](docs/STARTUP_GUIDE.md)** - Detailed setup instructions
- **[Network Setup](docs/NETWORK_SETUP.md)** - Network configuration
- **[Security Guidelines](SECURITY.md)** - Security best practices
- **[Image Loading Fix](docs/IMAGE_LOADING_FIX.md)** - Troubleshooting image issues
- **[Image Rendering Fixes](docs/IMAGE_RENDERING_FIXES.md)** - Image rendering solutions
- **[Hierarchical Tagging Guide](docs/HIERARCHICAL_TAGGING_GUIDE.md)** - Advanced annotation

## 🔒 Security

This project follows security best practices:
- Environment variables for sensitive configuration
- User data excluded from git
- Comprehensive `.gitignore` for secrets and keys

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com/) for YOLOv8
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [React](https://reactjs.org/) for the UI library

## 📞 Support

For support, email support@shrimpvision.com or create an issue on GitHub.

---

**Made with ❤️ for the aquaculture and computer vision community**
