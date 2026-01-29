# 🚀 Shrimp Vision Quick Start Guide

Get up and running with Shrimp Vision in under 5 minutes!

## 📋 Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Docker** (optional, for containerized deployment)

## ⚡ Quick Setup

### Option 1: Docker (Recommended for Production)

The easiest way to run Shrimp Vision is with Docker:

```bash
git clone <repository-url>
cd shrimp-vision
# Run in foreground (see logs)
docker-compose up --build

# Or run in background (headless/detached mode)
docker-compose up -d --build
```

Access the application at:
- **Frontend**: http://localhost:3099
- **Backend API**: http://localhost:3100
- **API Docs**: http://localhost:3100/docs

See [Docker Setup Guide](docs/DOCKER.md) for more details.

### Option 2: Automated Script (Development)

**For macOS/Linux:**
```bash
git clone <repository-url>
cd shrimp-vision
chmod +x start.sh
./start.sh
```

**For Windows:**
```cmd
git clone <repository-url>
cd shrimp-vision
scripts\start.bat
```

The script will automatically:
- Check prerequisites
- Set up virtual environment
- Install dependencies
- Start both backend and frontend servers

### Option 3: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shrimp-vision
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```
   Backend runs on: `http://localhost:3100`

3. **Set up the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend runs on: `http://localhost:3099`

4. **Open your browser**
   Navigate to `http://localhost:3099` to start using Shrimp Vision!

## 🎯 First Steps

### 1. Upload Your First Images
- Go to the **Upload** page
- Drag & drop 5-10 aquarium images
- Supported formats: JPG, PNG, WEBP, HEIC, BMP, TIFF

### 2. Annotate Shrimp
- Navigate to **Annotate**
- Select a class from the buttons (Shrimp, Juvenile, Adult, Egg, Molt, Dead)
- Draw bounding boxes around each shrimp
- Save your annotations

### 3. Train Your Model
- Visit the **Train** page
- Select YOLOv8n (fastest) for your first model
- Click "Start Training"
- Monitor progress in real-time
- Wait 10-30 minutes for training to complete

### 4. Test Your Model
- Go to the **Test** page
- Upload a new image
- Select your trained model
- Adjust confidence threshold
- See your model detect shrimp!

## 🎨 What You'll See

- **Beautiful UI**: Modern, responsive design with Tailwind CSS
- **Real-time Progress**: Live training metrics and progress bars
- **Interactive Tools**: Drag-and-drop annotation with visual feedback
- **Multi-class Support**: 6 different shrimp classes with color coding
- **Export Options**: Download models and datasets

## 🔧 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (needs 3.11+)
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Check port 3100 is available: `lsof -i:3100` (macOS/Linux) or `netstat -ano | findstr :3100` (Windows)

**Frontend won't start?**
- Check Node version: `node --version` (needs 18+)
- Install dependencies: `cd frontend && npm install`
- Check port 3099 is available

**Training fails?**
- Ensure you have at least 5 annotated images
- Check available disk space (need 2GB+)
- Verify you have enough RAM (4GB+ recommended)

**Docker issues?**
- Ensure Docker and Docker Compose are installed
- Check ports 3099 and 3100 are not in use
- See [Docker Setup Guide](docs/DOCKER.md) for detailed troubleshooting

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [Docker setup](docs/DOCKER.md) for containerized deployment
- See [Startup Guide](docs/STARTUP_GUIDE.md) for detailed instructions
- Review [Security Guidelines](SECURITY.md) for best practices
- Check out the [API docs](http://localhost:3100/docs) when running
- Explore different YOLOv8 model sizes for your use case

## 🆘 Need Help?

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the troubleshooting section in the main README
- Check the [Startup Guide](docs/STARTUP_GUIDE.md) for common issues
- Make sure all prerequisites are installed correctly

---

**Happy shrimp detecting! 🦐✨**
