# Brev Launchable Selection Guide
## Communication Bridge AI - NVIDIA GPU Deployment

You're at the "Select a Launchable" step. Here's what to do:

---

## 🎯 Recommended Approach

Since none of the pre-built launchables match your Communication Bridge AI project, you have two options:

### Option 1: Skip Launchables (Recommended)

1. Look for "Skip" or "None" or "Custom" option
2. Or click "Back" to return to the previous screen
3. Look for "Add a setup script" option
4. Upload or paste the `brev_setup_script.sh` content

### Option 2: Use a Basic Launchable

If you must choose one from the list, pick the simplest one that:
- Has Python 3.10+
- Has CUDA support
- Is cheapest (around $0.48-0.56/hr)

From your list, these might work:
- **"Llama Nemotron Nano VL 8B"** ($0.48/hr) - Has LLM support
- **"CATE"** ($0.48/hr) - Has CUDA acceleration

But you'll still need to install your dependencies manually.

---

## 🚀 What to Do After Selecting

### If You Skip Launchables:

1. **Upload setup script:**
   - Use the `brev_setup_script.sh` I created
   - Or paste it in the "Add a setup script" field

2. **Deploy the instance**

3. **Wait for provisioning** (5-7 minutes)

4. **Connect via SSH or web terminal**

### If You Choose a Launchable:

1. **Select the cheapest one** with Python/CUDA

2. **Deploy the instance**

3. **Connect and run manual setup:**
   ```bash
   # Update system
   sudo apt-get update && sudo apt-get upgrade -y
   
   # Install dependencies
   pip install fastapi uvicorn mediapipe opencv-python
   
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Clone your repo
   git clone https://github.com/YOUR_USERNAME/communication-bridge-ai.git
   ```

---

## 📋 Manual Setup Steps (If No Script)

Once your instance is running, connect and run:

```bash
# 1. Verify GPU
nvidia-smi

# 2. Install Python packages
pip install fastapi uvicorn pydantic python-multipart bcrypt PyJWT google-generativeai

# 3. Install GPU libraries
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install mediapipe opencv-python openai-whisper

# 4. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 5. Start Ollama
ollama serve &

# 6. Download Llama 3
ollama pull llama3

# 7. Clone your project
git clone https://github.com/YOUR_USERNAME/communication-bridge-ai.git
cd communication-bridge-ai

# 8. Create .env file
nano .env
# Add your GEMINI_API_KEY and JWT_SECRET

# 9. Start backend
cd backend
python main.py
```

---

## 💡 Pro Tips

### Cost Optimization:
- Choose the **$0.48/hr** options (cheapest T4 GPU)
- Stop instance when not using it
- Set up billing alerts

### Time Saving:
- Have your GitHub repo ready
- Have your .env variables ready to paste
- Use tmux to keep processes running

### Troubleshooting:
- If launchable fails, just skip it and do manual setup
- Manual setup takes 10-15 minutes
- Automated script takes 5-10 minutes

---

## 🎯 Quick Decision Matrix

| Scenario | What to Do |
|----------|------------|
| "Skip" option available | ✅ Skip and use custom script |
| Must choose launchable | Choose cheapest ($0.48/hr) |
| Launchable fails | Do manual setup |
| Unsure | Skip and do manual setup |

---

## 📞 Need Help?

If you're stuck:

1. **Try to skip the launchable selection**
2. **Or choose the cheapest one and do manual setup**
3. **The setup script I created has everything you need**

---

## ✅ What You Need

Your instance needs:
- ✅ T4 GPU (16GB VRAM) - You already selected this
- ✅ Ubuntu 22.04 - Should be default
- ✅ Python 3.10+ - Will install
- ✅ CUDA drivers - Should be pre-installed
- ✅ Your project dependencies - Will install

---

## 🚀 Next Steps

1. **Make your choice** (skip or select cheapest)
2. **Click Deploy**
3. **Wait for instance to start**
4. **Follow NVIDIA_BREV_SETUP.md** for detailed setup

The launchable is just a starting point - you'll customize it anyway!
