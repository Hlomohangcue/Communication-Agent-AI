#!/bin/bash
# Communication Bridge AI - NVIDIA GPU Setup Script
# This script sets up your environment on Brev with all dependencies

set -e  # Exit on error

echo "=========================================="
echo "Communication Bridge AI - GPU Setup"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential tools
echo "🔧 Installing essential tools..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    python3-pip \
    python3-venv \
    tmux \
    htop

# Verify GPU
echo "🎮 Verifying GPU access..."
nvidia-smi

# Install Python dependencies
echo "🐍 Setting up Python environment..."
python3 -m pip install --upgrade pip

# Install core dependencies
echo "📚 Installing Python packages..."
pip install \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.1 \
    pydantic==2.10.3 \
    python-multipart==0.0.20 \
    bcrypt==4.1.2 \
    PyJWT==2.8.0 \
    google-generativeai==0.8.3 \
    requests==2.32.3 \
    numpy==1.24.3

# Install GPU libraries
echo "🚀 Installing GPU-accelerated libraries..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install AI/ML libraries
echo "🤖 Installing AI/ML libraries..."
pip install \
    mediapipe==0.10.8 \
    opencv-python==4.8.1.78 \
    openai-whisper \
    transformers \
    accelerate

# Install Ollama for local LLM
echo "🦙 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Verify installations
echo "✅ Verifying installations..."
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
python3 -c "import mediapipe; print('MediaPipe: OK')"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clone your repo: git clone <your-repo-url>"
echo "2. Start Ollama: ollama serve &"
echo "3. Download model: ollama pull llama3"
echo "4. Run your app: cd backend && python main.py"
echo ""
echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
