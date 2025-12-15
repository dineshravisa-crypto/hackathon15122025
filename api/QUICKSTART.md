# Quick Start Guide - 5 Minutes to Running

This guide will get you up and running with the Commander Data Agent API in just a few minutes.

## Prerequisites

- ✅ Python 3.10 or higher installed
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step 1: Set Up Environment (2 minutes)

### On Windows:

```cmd
cd GenAI\api
copy env.example .env
notepad .env
```

### On macOS/Linux:

```bash
cd GenAI/api
cp env.example .env
nano .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

💡 **Tip**: You can skip `TAVILY_API_KEY` for now (web search won't work, but everything else will)

## Step 2: Run the Server (1 minute)

### Option A: Using Quick Start Scripts (Easiest)

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create a virtual environment
- Install all dependencies
- Start the server

### Option B: Manual Start

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## Step 3: Test with Postman (2 minutes)

### Quick Setup:

1. **Open Postman**
2. **Import Collection**:
   - Click "Import" button
   - Select `Data_Agent_API.postman_collection.json`
   - Click "Import"

3. **Send Your First Request**:
   - Open "Chat" → "1. Greeting"
   - Click "Send"
   - You should see Data's response!

### Test Without Postman:

Use curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello Commander Data!\", \"session_id\": \"test\"}"
```

Or run the test script:

```bash
python test_api.py
```

## Step 4: Explore the API

Open your browser to see the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from your browser!

## Common Test Messages

Try these in Postman or the browser docs:

### Basic Greeting
```json
{
  "message": "Hello Commander Data!",
  "session_id": "my-session"
}
```

### Math Calculation
```json
{
  "message": "What is 25 multiplied by 4?",
  "session_id": "my-session"
}
```

### Ask About Data
```json
{
  "message": "Who created you?",
  "session_id": "my-session"
}
```

### Test Memory
```json
{
  "message": "What did I just ask you?",
  "session_id": "my-session"
}
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you created `.env` file
- Check that your API key starts with `sk-`

### "Port 8000 already in use"
Edit `main.py` and change the port:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### "No module named 'fastapi'"
Make sure you activated the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Then install dependencies:
```bash
pip install -r requirements.txt
```

## What's Next?

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🧪 Run `python test_api.py` to test all features
- 🔍 Explore the interactive docs at http://localhost:8000/docs
- 🌐 Add `TAVILY_API_KEY` to enable web search

## Need Help?

- Check the console output for error messages
- Ensure Python 3.10+ is installed: `python --version`
- Verify your OpenAI API key is valid
- Make sure port 8000 is available

Enjoy chatting with Commander Data! 🖖

