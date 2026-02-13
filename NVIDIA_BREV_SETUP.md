# NVIDIA Brev GPU Instance Setup Guide
## Communication Bridge AI - GPU Deployment

This guide walks you through setting up your GPU instance on Brev using your NVIDIA credits.

---

## 🎯 Prerequisites

Before starting, make sure you have:
- [ ] NVIDIA GPU credits ($60 from LabLab hackathon)
- [ ] Brev account (we'll create this)
- [ ] Your project code ready (current Communication Bridge AI)
- [ ] Git installed locally
- [ ] Basic terminal/command line knowledge

---

## Step 1: Redeem NVIDIA Credits (5 minutes)

1. **Click the redemption link** from your LabLab email:
   ```
   👉 Redeem NVIDIA Credits
   ```

2. **Follow the redemption process:**
   - You'll be directed to Brev's website
   - Sign up or log in to Brev
   - Credits will be automatically applied to your account

3. **Verify credits:**
   - Go to Brev dashboard
   - Check "Billing" or "Credits" section
   - You should see $60 in credits

---

## Step 2: Create Brev Account (5 minutes)

If you don't have a Brev account yet:

1. **Go to:** https://brev.dev
2. **Sign up with:**
   - Email (recommended)
   - GitHub account
   - Google account

3. **Complete profile:**
   - Name
   - Organization (optional - can use "Personal" or "LabLab Hackathon")
   - Use case: "AI/ML Development"

---

## Step 3: Launch GPU Instance (10 minutes)

### Choose Your GPU

For your project, I recommend:

**Option A: NVIDIA T4 (Budget-Friendly)**
- Cost: ~$0.50-0.70/hour
- VRAM: 16GB
- Good for: LLM inference, computer vision
- Best for: Development and testing

**Option B: NVIDIA A10 (Balanced)**
- Cost: ~$1.00-1.50/hour
- VRAM: 24GB
- Good for: Everything + faster inference
- Best for: Production demos

**Option C: NVIDIA A100 (Premium)**
- Cost: ~$2.00-3.00/hour
- VRAM: 40GB or 80GB
- Good for: Heavy training, multiple models
- Best for: If you want to train custom models

**Recommendation:** Start with T4 for development, upgrade to A10 for demo day.

### Launch Instance

1. **In Brev Dashboard:**
   - Click "New Instance" or "Launch"
   - Select "GPU Instance"

2. **Configure Instance:**
   ```
   Name: communication-bridge-gpu
   GPU Type: NVIDIA T4 (or A10)
   Region: US-West (or closest to you)
   OS: Ubuntu 22.04 LTS
   Storage: 50GB (minimum)
   ```

3. **Select Software Stack:**
   - Choose "Python 3.10" or "PyTorch" template
   - This pre-installs CUDA, Python, and common ML libraries

4. **Click "Launch Instance"**
   - Wait 2-5 minutes for provisioning
   - You'll get SSH access details

---

## Step 4: Connect to Your Instance (5 minutes)

### Option A: Brev Web Terminal (Easiest)

1. In Brev dashboard, click your instance
2. Click "Open Terminal" or "Connect"
3. You're in! Skip to Step 5.

### Option B: SSH from Your Computer

1. **Get SSH command from Brev:**
   ```bash
   ssh -i ~/.ssh/brev_key user@your-instance-ip
   ```

2. **On Windows (using PowerShell or CMD):**
   ```powershell
   ssh user@your-instance-ip
   ```

3. **Enter password** (provided by Brev)

---

## Step 5: Verify GPU Access (2 minutes)

Once connected, run:

```bash
# Check GPU
nvidia-smi
```

You should see output like:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.xx.xx    Driver Version: 525.xx.xx    CUDA Version: 12.0   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
| N/A   45C    P0    28W /  70W |      0MiB / 15360MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

**If you see this, your GPU is ready!** ✅

---

## Step 6: Install System Dependencies (10 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install build tools
sudo apt install build-essential -y

# Install CUDA toolkit (if not pre-installed)
# Usually pre-installed on Brev, but verify:
nvcc --version
```

---

## Step 7: Clone Your Project (5 minutes)

### Option A: From GitHub (if you pushed it)

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/communication-bridge-ai.git
cd communication-bridge-ai
```

### Option B: Upload from Local Machine

**On your local machine:**
```bash
# Create a zip of your project
# (Exclude node_modules, __pycache__, .git if large)
```

**Then upload to instance:**
```bash
# On Brev instance
mkdir communication-bridge-ai
cd communication-bridge-ai

# Use scp or Brev's file upload feature
```

### Option C: Fresh Setup (if needed)

```bash
mkdir communication-bridge-ai
cd communication-bridge-ai

# We'll recreate the structure in the next guides
```

---

## Step 8: Setup Python Environment (5 minutes)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install current requirements
pip install -r requirements.txt
```

---

## Step 9: Configure Environment Variables (3 minutes)

```bash
# Create .env file
nano .env
```

Add your configuration:
```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET=your_jwt_secret_here
DATABASE_URL=sqlite:///./communication_bridge.db
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 10: Test Current System (5 minutes)

Before adding GPU features, verify your current system works:

```bash
# Start backend
cd backend
python main.py
```

In another terminal (or use tmux/screen):
```bash
# Test API
curl http://localhost:8000/
```

You should see:
```json
{"status": "Communication Bridge AI is running", "version": "1.0.0"}
```

**If this works, you're ready for GPU enhancements!** ✅

---

## Step 11: Install GPU-Specific Libraries (10 minutes)

Now let's add the GPU libraries we'll need:

```bash
# Make sure venv is activated
source venv/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Transformers (for LLMs)
pip install transformers accelerate

# Install Ollama (for local LLM)
curl -fsSL https://ollama.com/install.sh | sh

# Install MediaPipe (for computer vision)
pip install mediapipe opencv-python

# Install Whisper (for speech-to-text)
pip install openai-whisper

# Verify installations
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
```

Expected output:
```
PyTorch: 2.x.x
CUDA Available: True
```

---

## Step 12: Download AI Models (15 minutes)

### Download Llama 3 (for local LLM)

```bash
# Start Ollama service
ollama serve &

# Download Llama 3 8B (recommended)
ollama pull llama3

# Or download Mistral 7B (alternative)
ollama pull mistral

# Test it
ollama run llama3 "Hello, how are you?"
```

### Download Whisper Model (for speech-to-text)

```bash
# This will auto-download on first use, but we can pre-download:
python -c "import whisper; whisper.load_model('base')"
```

---

## Step 13: Verify GPU Setup (5 minutes)

Create a test script:

```bash
nano test_gpu.py
```

Add:
```python
import torch
import whisper
import mediapipe as mp

print("=== GPU Setup Verification ===")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

print("\n=== Testing Whisper ===")
model = whisper.load_model("base")
print(f"Whisper Model Loaded: {model.device}")

print("\n=== Testing MediaPipe ===")
mp_hands = mp.solutions.hands
print("MediaPipe Hands: OK")

print("\n✅ All GPU components ready!")
```

Run it:
```bash
python test_gpu.py
```

---

## Step 14: Setup Process Manager (Optional but Recommended)

To keep your server running:

```bash
# Install tmux or screen
sudo apt install tmux -y

# Create a tmux session
tmux new -s communication-bridge

# Your server will keep running even if you disconnect
# To detach: Ctrl+B, then D
# To reattach: tmux attach -s communication-bridge
```

---

## 🎉 Setup Complete!

Your GPU instance is now ready with:
- ✅ NVIDIA GPU (T4/A10/A100)
- ✅ CUDA and PyTorch
- ✅ Ollama with Llama 3
- ✅ MediaPipe for computer vision
- ✅ Whisper for speech-to-text
- ✅ Your current Communication Bridge AI code

---

## 💰 Cost Management Tips

### Monitor Your Usage

```bash
# Check GPU usage
watch -n 1 nvidia-smi

# Check Brev credits
# Go to Brev dashboard > Billing
```

### Save Money

1. **Stop instance when not using:**
   - Brev dashboard > Your instance > Stop
   - You only pay when running

2. **Use spot instances:**
   - Cheaper but can be interrupted
   - Good for development

3. **Set spending alerts:**
   - Brev dashboard > Billing > Alerts
   - Get notified at $10, $30, $50

4. **Optimize model sizes:**
   - Use smaller models during development
   - Llama 3 8B instead of 70B
   - Whisper base instead of large

---

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Reinstall NVIDIA drivers
sudo apt install nvidia-driver-525 -y
sudo reboot
```

### CUDA Out of Memory

```bash
# Check what's using GPU
nvidia-smi

# Kill processes if needed
kill -9 <PID>

# Use smaller models
ollama pull llama3:8b  # Instead of larger versions
```

### Ollama Not Starting

```bash
# Check if running
ps aux | grep ollama

# Restart service
pkill ollama
ollama serve &
```

### SSH Connection Issues

```bash
# Check instance status in Brev dashboard
# Restart instance if needed
# Verify firewall rules allow SSH (port 22)
```

---

## 📊 Resource Usage Estimates

### With T4 GPU ($0.60/hour):
- **Development (8 hours):** $4.80
- **Testing (4 hours):** $2.40
- **Demo prep (4 hours):** $2.40
- **Hackathon demo (2 hours):** $1.20
- **Buffer (10 hours):** $6.00
- **Total:** ~$17 of your $60 credits

**You'll have $43 left for experimentation!**

---

## 🚀 Next Steps

Now that your GPU instance is set up, proceed to:

1. **LOCAL_LLM_INTEGRATION.md** - Replace Gemini with Llama 3
2. **COMPUTER_VISION_GUIDE.md** - Add webcam gesture detection
3. **SPEECH_TO_TEXT_GUIDE.md** - Add Whisper for speech recognition

---

## 📞 Support

### Brev Support:
- Documentation: https://brev.dev/docs
- Discord: https://discord.gg/brev
- Email: support@brev.dev

### LabLab Support:
- Discord: Check your hackathon Discord
- Email: support@lablab.ai

### NVIDIA Resources:
- CUDA Documentation: https://docs.nvidia.com/cuda/
- Developer Forums: https://forums.developer.nvidia.com/

---

## ✅ Checklist

Before moving to the next guide, verify:

- [ ] GPU instance is running
- [ ] `nvidia-smi` shows your GPU
- [ ] Python environment is activated
- [ ] Current system runs successfully
- [ ] PyTorch detects CUDA
- [ ] Ollama is installed and running
- [ ] Llama 3 model is downloaded
- [ ] MediaPipe is installed
- [ ] Whisper is installed
- [ ] You have credits remaining

**All checked? Great! You're ready for GPU enhancements!** 🎉
