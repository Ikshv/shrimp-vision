#!/bin/bash

# Update HEIC Support Script
# Installs pillow-heif and restarts backend

echo "📱 Adding iPhone HEIC Support..."
echo "==============================="

# Install pillow-heif
echo "📦 Installing pillow-heif for iPhone photo support..."
cd backend
source venv/bin/activate
pip install pillow-heif

echo "✅ HEIC support installed!"
echo ""
echo "🔄 Restart your backend server to apply changes:"
echo "   cd backend && source venv/bin/activate && python run.py"
echo ""
echo "📱 iPhone photos (HEIC format) are now supported!"
