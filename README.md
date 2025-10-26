# 🦐 Shrimp Vision - AI Shrimp Detection System

A complete full-stack application for shrimp detection and counting using computer vision. Upload aquarium images, annotate shrimp, train YOLOv8 models, and deploy for real-time detection.

![Shrimp Vision](https://img.shields.io/badge/Shrimp-Vision-orange?style=for-the-badge&logo=shrimp)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red?style=for-the-badge)

## ✨ Features

### 🖼️ Image Management
- **Drag & Drop Upload**: Upload multiple aquarium images with support for JPG, PNG, BMP, TIFF
- **Image Preview**: Thumbnail grid with image metadata (dimensions, file size, format)
- **Batch Processing**: Handle multiple images simultaneously
- **Image Validation**: Automatic format and size validation

### 🎯 Annotation Tool
- **Interactive Bounding Boxes**: Click and drag to draw precise bounding boxes around shrimp
- **Real-time Feedback**: Visual feedback with labeled annotations
- **Navigation**: Easy previous/next navigation between images
- **Auto-save**: Automatic saving of annotation progress
- **Statistics**: Real-time count of annotated shrimp and progress tracking

### 🧠 Model Training
- **YOLOv8 Integration**: Support for all YOLOv8 model sizes (nano, small, medium, large, xlarge)
- **Live Training Progress**: Real-time monitoring of training metrics (loss, accuracy, epochs)
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

## 🏗️ Architecture

```
Shrimp Vision/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── routes/             # API route handlers
│   │   ├── upload.py       # Image upload endpoints
│   │   ├── annotate.py     # Annotation management
│   │   ├── train.py        # Model training endpoints
│   │   ├── inference.py    # Model inference endpoints
│   │   └── export.py       # Data export endpoints
│   ├── services/           # Core business logic
│   │   ├── dataset_manager.py    # Dataset preparation and management
│   │   ├── model_trainer.py      # YOLOv8 training pipeline
│   │   └── inference_engine.py   # Model inference engine
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js 13+ app directory
│   │   ├── page.tsx       # Home page
│   │   ├── upload/        # Image upload page
│   │   ├── annotate/      # Annotation tool page
│   │   ├── train/         # Model training page
│   │   └── test/          # Testing and export page
│   ├── lib/               # Utility functions
│   │   ├── api.ts         # API client configuration
│   │   └── utils.ts       # Helper functions
│   └── package.json       # Node.js dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git** for cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SKRIMP
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

4. **Create environment file**
   ```bash
   # In frontend directory
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The web application will be available at `http://localhost:3000`

3. **Open your browser**
   Navigate to `http://localhost:3000` to start using Shrimp Vision!

## 📖 Usage Guide

### 1. Upload Images
- Navigate to the **Upload** page
- Drag and drop aquarium images or click to select files
- Supported formats: JPG, PNG, BMP, TIFF
- Recommended: High-resolution images (640×640+ pixels) with good lighting

### 2. Annotate Shrimp
- Go to the **Annotate** page
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
- Click "Start Training" and monitor progress
- Training typically takes 10-60 minutes depending on dataset size

### 4. Test & Export
- Go to the **Test** page
- Select a trained model and upload a test image
- Adjust confidence threshold as needed
- View detection results with bounding boxes
- Export your trained model or complete dataset

## 🔧 Configuration

### Backend Configuration

The backend can be configured by modifying environment variables or the main configuration in `backend/main.py`:

```python
# Training defaults
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 16
DEFAULT_IMAGE_SIZE = 640
DEFAULT_LEARNING_RATE = 0.01

# Dataset splitting
DEFAULT_TRAIN_SPLIT = 0.8
DEFAULT_VAL_SPLIT = 0.2
```

### Frontend Configuration

Frontend configuration is handled through environment variables in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

## 📊 API Documentation

### Upload Endpoints
- `POST /api/upload/` - Upload multiple images
- `GET /api/upload/list` - List uploaded images
- `DELETE /api/upload/{id}` - Delete an image

### Annotation Endpoints
- `POST /api/annotate/save` - Save annotation for an image
- `GET /api/annotate/{id}` - Get annotation for an image
- `GET /api/annotate/stats/summary` - Get annotation statistics

### Training Endpoints
- `POST /api/train/start` - Start model training
- `GET /api/train/status` - Get training status
- `POST /api/train/stop` - Stop training

### Inference Endpoints
- `POST /api/inference/predict` - Run inference on an image
- `GET /api/inference/models/available` - List available models

### Export Endpoints
- `POST /api/export/dataset` - Export complete dataset
- `GET /api/export/model/{name}` - Download a specific model

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py  # Development server with auto-reload
```

### Frontend Development

```bash
cd frontend
npm run dev     # Development server with hot reload
npm run build   # Production build
npm run start   # Production server
```

### Code Structure

- **Backend**: FastAPI with async/await patterns, Pydantic models for validation
- **Frontend**: Next.js 13+ with App Router, TypeScript, Tailwind CSS
- **State Management**: React hooks with local state
- **API Communication**: Axios with interceptors for error handling
- **UI Components**: Custom components with Tailwind CSS styling

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/  # Run backend tests
```

### Frontend Testing
```bash
cd frontend
npm test  # Run frontend tests
```

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
- Verify port 8000 is not in use

**Frontend won't start**
- Ensure Node.js 18+ is installed
- Install dependencies: `npm install`
- Check that port 3000 is not in use

**Training fails**
- Ensure you have at least 5 annotated images
- Check available disk space (need at least 2GB)
- Verify CUDA installation if using GPU

**Inference is slow**
- Try using a smaller model (yolov8n)
- Reduce image size in training configuration
- Use GPU for inference if available

### Getting Help

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review the API documentation at `http://localhost:8000/docs`
3. Check browser console for frontend errors
4. Check backend logs for server errors

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
