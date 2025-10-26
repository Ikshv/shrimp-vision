# 🚀 Shrimp Vision Quick Start Guide

Get up and running with Shrimp Vision in under 5 minutes!

## 📋 Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

## ⚡ Quick Setup

### Option 1: Automated Setup (Recommended)

**For macOS/Linux:**
```bash
git clone <repository-url>
cd SKRIMP
chmod +x start.sh
./start.sh
```

**For Windows:**
```cmd
git clone <repository-url>
cd SKRIMP
start.bat
```

### Option 2: Manual Setup

1. **Clone and setup backend:**
   ```bash
   git clone <repository-url>
   cd SKRIMP/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

2. **Setup frontend (in new terminal):**
   ```bash
   cd SKRIMP/frontend
   npm install
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🎯 First Steps

### 1. Upload Your First Images
- Go to the **Upload** page
- Drag & drop 5-10 aquarium images
- Supported formats: JPG, PNG, BMP, TIFF

### 2. Annotate Shrimp
- Navigate to **Annotate**
- Draw bounding boxes around each shrimp
- Save your annotations

### 3. Train Your Model
- Visit the **Train** page
- Select YOLOv8n (fastest) for your first model
- Click "Start Training"
- Wait 10-30 minutes for training to complete

### 4. Test Your Model
- Go to **Test & Export**
- Upload a new image
- See your model detect shrimp!

## 🎨 What You'll See

- **Beautiful UI**: Modern, responsive design with Tailwind CSS
- **Real-time Progress**: Live training metrics and progress bars
- **Interactive Tools**: Drag-and-drop annotation with visual feedback
- **Export Options**: Download models and datasets

## 🔧 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Check Node version: `node --version`
- Install dependencies: `npm install`

**Training fails?**
- Ensure you have at least 5 annotated images
- Check available disk space (need 2GB+)

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [API docs](http://localhost:8000/docs) when running
- Explore different YOLOv8 model sizes for your use case
- Try batch processing multiple images

## 🆘 Need Help?

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the troubleshooting section in the main README
- Make sure all prerequisites are installed correctly

---

**Happy shrimp detecting! 🦐✨**
