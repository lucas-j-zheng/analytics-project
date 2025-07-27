# 🤖 Local AI Setup Guide for Football Analytics Platform

## 🎯 **Current Status**
Your platform now supports **hybrid AI**:
- ✅ **Fallback Mode**: Basic pattern-matching responses (currently active)
- 🚀 **Enhanced Mode**: Local AI with Ollama (ready to install)

---

## 🚀 **Option 1: Ollama (Recommended)**

### **Installation**
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### **Setup Models**
```bash
# Start Ollama service
ollama serve

# In another terminal, pull models
ollama pull llama3.1:8b          # Best balance (4GB RAM)
ollama pull phi3:3.8b            # Lightweight (2GB RAM)  
ollama pull mistral:7b           # Fast and efficient (4GB RAM)
ollama pull codellama:7b         # Best for data analysis (4GB RAM)
```

### **Test Installation**
```bash
# Test if working
curl http://localhost:11434/api/tags

# Should return list of installed models
```

---

## 🐳 **Option 2: LocalAI (Docker)**

### **Quick Setup**
```bash
# Pull and run LocalAI
docker run -p 8080:8080 --name local-ai -d localai/localai:latest
```

### **Update Backend Config**
```python
# In backend/ai_local.py, change:
self.base_url = "http://localhost:8080"  # Instead of 11434
```

---

## 🔧 **Option 3: Llama.cpp (Advanced)**

### **Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download model
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Run server
./server -m Phi-3-mini-4k-instruct-q4.gguf -c 2048 --host 0.0.0.0 --port 11434
```

---

## 📊 **Model Recommendations by Hardware**

### **8GB RAM or Less**
```bash
ollama pull phi3:3.8b            # 2GB, very capable
ollama pull llama3.1:8b          # 4GB, excellent for analytics
```

### **16GB RAM**
```bash
ollama pull mistral:7b           # 4GB, fast
ollama pull codellama:13b        # 7GB, best for structured data
```

### **32GB+ RAM**
```bash
ollama pull llama3.1:70b         # 40GB, GPT-4 level quality
ollama pull codellama:34b        # 19GB, enterprise-grade analysis
```

---

## 🧪 **Testing Your Setup**

### **1. Check AI Status**
```bash
curl http://127.0.0.1:5001/api/ai/status
```

### **2. Test AI Query**
1. Go to http://localhost:3001
2. Login as team
3. Click "Ask AI Assistant"  
4. Try: "What insights can you provide about our team performance?"

### **3. Expected Behavior**
- **Without Ollama**: Gets basic pattern-matching responses
- **With Ollama**: Gets intelligent AI analysis of your actual game data

---

## ⚡ **Performance Comparison**

| Setup | Response Time | Quality | RAM Usage | Setup Time |
|-------|---------------|---------|-----------|------------|
| **No AI** | <100ms | Basic | 0MB | 0 min |
| **Ollama + Phi3** | 2-5s | Good | 2GB | 10 min |
| **Ollama + Llama3.1** | 3-8s | Excellent | 4GB | 10 min |
| **LocalAI** | 2-6s | Good | 4GB | 5 min |
| **OpenAI API** | 1-3s | Excellent | 0MB | 2 min |

---

## 🎯 **Quick Start (5 Minutes)**

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start service (in background)
ollama serve &

# 3. Pull lightweight model
ollama pull phi3:3.8b

# 4. Test your platform
# Go to http://localhost:3001 and try the AI assistant!
```

---

## 🔍 **Troubleshooting**

### **Ollama Not Starting**
```bash
# Check if port is in use
lsof -i :11434

# Kill existing process
pkill ollama

# Restart
ollama serve
```

### **Out of Memory**
```bash
# Use smaller model
ollama pull phi3:3.8b

# Or add swap space (Linux)
sudo swapon --show
```

### **Slow Responses**
- Use GPU acceleration if available
- Choose smaller models (phi3 vs llama3.1)
- Increase system RAM

---

## 💡 **Pro Tips**

1. **Start Small**: Begin with `phi3:3.8b` to test
2. **GPU Boost**: Install CUDA/ROCm for 10x speed improvement
3. **Multiple Models**: Keep both lightweight and powerful models
4. **Memory Management**: Monitor RAM usage with `htop`
5. **Background Service**: Set Ollama to start on boot

---

## 🎉 **What You Get**

Once set up, your AI assistant will provide:
- ✅ **Intelligent game analysis** based on actual data
- ✅ **Formation recommendations** with specific stats  
- ✅ **Trend analysis** across multiple games
- ✅ **Natural language understanding** for complex queries
- ✅ **Privacy**: All data stays on your machine
- ✅ **Cost**: $0 after initial setup

**Your platform is ready for AI enhancement!** 🏈🤖