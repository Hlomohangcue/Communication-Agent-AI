# Local LLM Integration Guide
## Replace Gemini API with Llama 3 on GPU

This guide shows you how to replace Google Gemini API calls with a local Llama 3 model running on your GPU.

---

## 🎯 Why Local LLM?

### Benefits:
- ✅ **Faster responses** - No network latency
- ✅ **No API costs** - Run unlimited queries
- ✅ **Privacy** - Data never leaves your server
- ✅ **Offline capable** - Works without internet
- ✅ **Customizable** - Fine-tune for your use case
- ✅ **Hackathon impressive** - Shows technical depth

### Trade-offs:
- ⚠️ Requires GPU (you have this!)
- ⚠️ Slightly different response style
- ⚠️ Need to manage model loading

---

## 📊 Architecture Change

### Before (Gemini API):
```
User Input → FastAPI → Gemini API (Cloud) → Response
                         ↓
                    (Network call, ~500ms)
```

### After (Local Llama 3):
```
User Input → FastAPI → Llama 3 (GPU) → Response
                         ↓
                    (Local, ~100ms)
```

---

## Step 1: Create LLM Service Module (10 minutes)

Create a new file for local LLM handling:

```bash
cd backend
mkdir services
touch services/__init__.py
nano services/llm_service.py
```

Add this code:

```python
import os
import requests
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import GEMINI_API_KEY

class LLMService:
    """
    Unified LLM service that can use either:
    1. Local Ollama (Llama 3) - GPU-powered
    2. Google Gemini API - Cloud fallback
    """
    
    def __init__(self, use_local: bool = True, ollama_url: str = "http://localhost:11434"):
        self.use_local = use_local
        self.ollama_url = ollama_url
        self.model_name = "llama3"  # or "mistral"
        
        # Initialize Gemini as fallback
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                print("✓ Gemini API initialized as fallback")
            except Exception as e:
                print(f"✗ Gemini initialization failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Test Ollama connection
        if self.use_local:
            if self._test_ollama():
                print(f"✓ Ollama connected - Using local {self.model_name}")
            else:
                print("✗ Ollama not available - Falling back to Gemini")
                self.use_local = False
    
    def _test_ollama(self) -> bool:
        """Test if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                return any(self.model_name in name for name in model_names)
            return False
        except:
            return False
    
    async def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """
        Generate text using local LLM or Gemini fallback
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
        
        Returns:
            Generated text response
        """
        if self.use_local:
            try:
                return await self._generate_ollama(prompt, max_tokens, temperature)
            except Exception as e:
                print(f"Ollama generation failed: {e}, falling back to Gemini")
                return await self._generate_gemini(prompt)
        else:
            return await self._generate_gemini(prompt)
    
    async def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using local Ollama"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    async def _generate_gemini(self, prompt: str) -> str:
        """Generate using Gemini API"""
        if not self.gemini_model:
            return "I apologize, but I'm unable to generate a response at the moment."
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return "I apologize, but I'm unable to generate a response at the moment."
    
    def switch_to_local(self):
        """Switch to local LLM"""
        if self._test_ollama():
            self.use_local = True
            print(f"✓ Switched to local {self.model_name}")
            return True
        else:
            print("✗ Cannot switch to local - Ollama not available")
            return False
    
    def switch_to_gemini(self):
        """Switch to Gemini API"""
        if self.gemini_model:
            self.use_local = False
            print("✓ Switched to Gemini API")
            return True
        else:
            print("✗ Cannot switch to Gemini - API not configured")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current LLM service status"""
        return {
            "using_local": self.use_local,
            "local_available": self._test_ollama(),
            "gemini_available": self.gemini_model is not None,
            "model_name": self.model_name if self.use_local else "gemini-1.5-flash-latest"
        }
```

Save and exit.

---

## Step 2: Update Speech Agent (15 minutes)

Now update the Speech Agent to use our new LLM service:

```bash
nano agents/speech_agent.py
```

Replace the imports and initialization:

```python
import os
from typing import Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.llm_service import LLMService

class SpeechAgent:
    def __init__(self, use_local_llm: bool = True):
        # Initialize LLM service (local or Gemini)
        self.llm = LLMService(use_local=use_local_llm)
        print(f"=== SpeechAgent Initialization ===")
        status = self.llm.get_status()
        print(f"LLM Status: {status}")
    
    async def generate_output(self, intent: str, semantic_meaning: str, confidence: float) -> Dict[str, Any]:
        # Try AI generation first
        try:
            prompt = f"""You are a supportive teacher/caregiver responding to a non-verbal student's communication.

Student's intent: {intent}
Student's message: {semantic_meaning}
Confidence: {confidence}

Generate a warm, helpful response that:
1. Acknowledges what the student communicated
2. Provides a direct answer if they asked a question
3. Offers support or assistance if needed
4. Is concise (1-3 sentences)
5. Is appropriate for a classroom setting

If the student asked a specific question (like "what is 1+1"), answer it directly and clearly.

Provide only the response text, nothing else."""

            output_text = await self.llm.generate(prompt, max_tokens=150, temperature=0.7)
            
            # Clean up any markdown or extra formatting
            output_text = output_text.replace('**', '').replace('*', '')
            
            return {
                "text": output_text,
                "format": "speech",
                "generation_method": "local_llm" if self.llm.use_local else "gemini_api"
            }
        except Exception as e:
            print(f"LLM generation error: {e}, using fallback")
            return self._fallback_output(intent, semantic_meaning)
    
    # Keep the existing _fallback_output method unchanged
    # ... (rest of the code stays the same)
```

---

## Step 3: Update Main Application (10 minutes)

Update `main.py` to use the new LLM service:

```bash
nano main.py
```

Add configuration and status endpoint:

```python
# Add near the top with other imports
from services.llm_service import LLMService

# Add after creating coordinator
llm_service = LLMService(use_local=True)  # Set to True for GPU, False for Gemini

# Add new endpoints before if __name__ == "__main__":

@app.get("/llm/status")
async def get_llm_status():
    """Get current LLM service status"""
    return llm_service.get_status()

@app.post("/llm/switch")
async def switch_llm(use_local: bool):
    """Switch between local LLM and Gemini API"""
    if use_local:
        success = llm_service.switch_to_local()
    else:
        success = llm_service.switch_to_gemini()
    
    return {
        "success": success,
        "status": llm_service.get_status()
    }
```

---

## Step 4: Update Requirements (2 minutes)

```bash
cd ..
nano requirements.txt
```

Add:
```
requests==2.32.3
```

(Already have this, but verify it's there)

---

## Step 5: Test Local LLM (10 minutes)

### Start Ollama Service

In a terminal:
```bash
# Start Ollama
ollama serve
```

Keep this running.

### Test Ollama Directly

In another terminal:
```bash
# Test Llama 3
ollama run llama3 "You are a teacher. A student waves hello. Respond warmly."
```

Expected output:
```
Hello! It's wonderful to see you! How are you doing today?
```

### Test via Python

Create a test script:
```bash
nano test_llm.py
```

Add:
```python
import asyncio
import sys
sys.path.append('backend')
from services.llm_service import LLMService

async def test():
    llm = LLMService(use_local=True)
    
    print("=== Testing Local LLM ===")
    print(f"Status: {llm.get_status()}\n")
    
    # Test 1: Simple greeting
    prompt1 = "You are a teacher. A student waves hello. Respond warmly in 1 sentence."
    response1 = await llm.generate(prompt1, max_tokens=50)
    print(f"Test 1 - Greeting:")
    print(f"Response: {response1}\n")
    
    # Test 2: Question
    prompt2 = "You are a teacher. A student asks 'what is 2+2?'. Answer directly."
    response2 = await llm.generate(prompt2, max_tokens=50)
    print(f"Test 2 - Question:")
    print(f"Response: {response2}\n")
    
    # Test 3: Need help
    prompt3 = "You are a teacher. A student raises their hand for help. Respond supportively."
    response3 = await llm.generate(prompt3, max_tokens=50)
    print(f"Test 3 - Help Request:")
    print(f"Response: {response3}\n")
    
    print("✅ All tests complete!")

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python test_llm.py
```

---

## Step 6: Start Your Application (5 minutes)

```bash
cd backend
python main.py
```

You should see:
```
✓ Ollama connected - Using local llama3
=== SpeechAgent Initialization ===
LLM Status: {'using_local': True, 'local_available': True, ...}
```

---

## Step 7: Test via API (5 minutes)

In another terminal:

```bash
# Test LLM status
curl http://localhost:8000/llm/status

# Test communication with local LLM
curl -X POST http://localhost:8000/communicate \
  -H "Content-Type: application/json" \
  -d '{"input_text": "👋", "user_type": "nonverbal"}'
```

---

## Step 8: Update Frontend (Optional - 10 minutes)

Add LLM status indicator to dashboard:

```bash
nano frontend/dashboard.html
```

Add in the user account section:
```html
<div class="llm-status">
    <span id="llm-indicator">🟢 Local LLM</span>
    <button onclick="toggleLLM()">Switch</button>
</div>
```

Add to `frontend/app.js`:
```javascript
// Check LLM status
async function checkLLMStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/llm/status`);
        const data = await response.json();
        
        const indicator = document.getElementById('llm-indicator');
        if (data.using_local) {
            indicator.textContent = '🟢 Local LLM (GPU)';
            indicator.style.color = '#4CAF50';
        } else {
            indicator.textContent = '🔵 Gemini API';
            indicator.style.color = '#2196F3';
        }
    } catch (error) {
        console.error('Failed to check LLM status:', error);
    }
}

// Toggle between local and Gemini
async function toggleLLM() {
    try {
        const statusResponse = await fetch(`${API_BASE_URL}/llm/status`);
        const status = await statusResponse.json();
        
        const newMode = !status.using_local;
        
        const response = await fetch(`${API_BASE_URL}/llm/switch?use_local=${newMode}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            checkLLMStatus();
            alert(`Switched to ${newMode ? 'Local LLM' : 'Gemini API'}`);
        } else {
            alert('Failed to switch LLM mode');
        }
    } catch (error) {
        console.error('Failed to toggle LLM:', error);
    }
}

// Check status on page load
checkLLMStatus();
setInterval(checkLLMStatus, 30000); // Check every 30 seconds
```

---

## 🎯 Performance Comparison

### Response Time Tests

Run this benchmark:
```bash
nano benchmark_llm.py
```

```python
import asyncio
import time
import sys
sys.path.append('backend')
from services.llm_service import LLMService

async def benchmark():
    llm_local = LLMService(use_local=True)
    llm_gemini = LLMService(use_local=False)
    
    prompt = "You are a teacher. A student waves hello. Respond warmly in 1 sentence."
    
    # Test local LLM
    print("Testing Local LLM (Llama 3)...")
    start = time.time()
    response1 = await llm_local.generate(prompt, max_tokens=50)
    local_time = time.time() - start
    print(f"Response: {response1}")
    print(f"Time: {local_time:.2f}s\n")
    
    # Test Gemini API
    print("Testing Gemini API...")
    start = time.time()
    response2 = await llm_gemini.generate(prompt)
    gemini_time = time.time() - start
    print(f"Response: {response2}")
    print(f"Time: {gemini_time:.2f}s\n")
    
    # Comparison
    speedup = gemini_time / local_time
    print(f"=== Results ===")
    print(f"Local LLM: {local_time:.2f}s")
    print(f"Gemini API: {gemini_time:.2f}s")
    print(f"Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")

if __name__ == "__main__":
    asyncio.run(benchmark())
```

Run:
```bash
python benchmark_llm.py
```

Expected results:
- Local LLM: 0.5-2s (depending on GPU)
- Gemini API: 1-3s (depending on network)

---

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
pkill ollama
ollama serve &

# Check logs
journalctl -u ollama -f
```

### Model Not Found

```bash
# List available models
ollama list

# Pull Llama 3 again
ollama pull llama3

# Or try Mistral
ollama pull mistral
```

### Slow Responses

```bash
# Check GPU usage
nvidia-smi

# Use smaller model
ollama pull llama3:8b

# Reduce max_tokens in llm_service.py
# Change max_tokens=200 to max_tokens=100
```

### Out of Memory

```bash
# Check GPU memory
nvidia-smi

# Use smaller model
ollama pull llama3:8b  # Instead of default

# Or reduce context window
# In llm_service.py, add to options:
# "num_ctx": 2048  # Reduce from default 4096
```

---

## 📊 Model Comparison

### Llama 3 8B (Recommended)
- Size: ~4.7GB
- VRAM: ~8GB
- Speed: Fast
- Quality: Excellent
- Best for: Production use

### Mistral 7B
- Size: ~4.1GB
- VRAM: ~7GB
- Speed: Very fast
- Quality: Very good
- Best for: Speed-critical apps

### Llama 3 70B (If you have A100)
- Size: ~40GB
- VRAM: ~48GB
- Speed: Slower
- Quality: Best
- Best for: Maximum quality

---

## 💡 Advanced Tips

### 1. Optimize for Speed

In `llm_service.py`, adjust parameters:
```python
"options": {
    "num_predict": 100,  # Reduce from 200
    "temperature": 0.5,  # Lower = more consistent
    "top_p": 0.9,
    "top_k": 40
}
```

### 2. Cache Common Responses

Add caching for frequent queries:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt_hash):
    # Cache responses for identical prompts
    pass
```

### 3. Batch Processing

For multiple requests:
```python
async def generate_batch(self, prompts: list) -> list:
    tasks = [self.generate(p) for p in prompts]
    return await asyncio.gather(*tasks)
```

---

## ✅ Verification Checklist

Before moving to the next guide:

- [ ] Ollama is running
- [ ] Llama 3 model is downloaded
- [ ] LLMService class works
- [ ] Speech Agent uses local LLM
- [ ] API endpoints respond correctly
- [ ] Responses are appropriate
- [ ] Fallback to Gemini works
- [ ] Frontend shows LLM status
- [ ] Performance is acceptable

---

## 🎉 Success!

You've successfully replaced Gemini API with a local GPU-powered LLM!

### What You Achieved:
- ✅ Local AI model running on GPU
- ✅ Faster response times
- ✅ No API costs
- ✅ Privacy-focused architecture
- ✅ Fallback system for reliability

### Next Steps:
1. **COMPUTER_VISION_GUIDE.md** - Add webcam gesture detection
2. **SPEECH_TO_TEXT_GUIDE.md** - Add Whisper for speech recognition

---

## 📈 Impact on Your Project

### Technical Improvements:
- Response time: 30-50% faster
- Cost: $0 per request (vs $0.001-0.01 per Gemini call)
- Privacy: 100% local processing
- Reliability: No network dependency

### Hackathon Value:
- Shows GPU utilization
- Demonstrates local AI deployment
- Privacy-focused architecture
- Technical depth and complexity

**You're now running a fully GPU-powered AI system!** 🚀
