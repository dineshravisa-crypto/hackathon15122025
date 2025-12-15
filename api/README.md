#  AgentEasy Agent API

A FastAPI application that creates an intelligent AI agent based on Lt.  AgentEasy from Star Trek: The Next Generation. The agent uses RAG (Retrieval-Augmented Generation) to access AgentEasy's dialogue history, can perform mathematical calculations, and search the web for current information.

## Features

- 🤖 **RAG-powered Memory**: Retrieves relevant dialogue from AgentEasy's past conversations
- 🧮 **Math Calculator**: Performs complex mathematical calculations
- 🌐 **Web Search**: Accesses current information via Tavily search API
- 💬 **Session Management**: Maintains conversation history per user session
- 🚀 **FastAPI**: Modern, fast, and well-documented REST API

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Tavily API key (optional, for web search) ([Get one here](https://tavily.com))

## Installation

### 1. Clone and Navigate to the API Directory

```bash
cd GenAI/api
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the `api` directory:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your API keys
```

Your `.env` file should look like this:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
TAVILY_API_KEY=tvly-your-actual-tavily-api-key-here
SCRIPT_DIRECTORY=./sample_AgentEasy/tng
```

⚠️ **Important**: 
- `OPENAI_API_KEY` is **required**
- `TAVILY_API_KEY` is **optional** (web search won't work without it)
- `SCRIPT_DIRECTORY` is **optional** (uses fallback AgentEasy if not found)

### 5. (Optional) Add Star Trek TNG Scripts

If you want the full AgentEasy experience, download the TNG scripts:

1. Get scripts from [ST-Minutiae.com](https://www.st-minutiae.com/resources/scripts/)
2. Create directory: `mkdir -p sample_AgentEasy/tng`
3. Extract script files to `sample_AgentEasy/tng/`

If you skip this step, the API will use sample fallback AgentEasy.

## Running the API

### Start the Server

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Initializing  AgentEasy Agent...
Extracted 6502 dialogue lines for AgentEasy
Agent initialization complete!
```

### Access the API

- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### 1. Health Check

**GET** `/`

Check if the API is running.

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "online",
  "message": " AgentEasy Agent API is running"
}
```

### 2. Chat with AgentEasy

**POST** `/chat`

Send a message to  AgentEasy.

**Request Body:**
```json
{
  "message": "Hello  AgentEasy!",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "response": "Greetings. How may I assist you today?",
  "session_id": "user123",
  "tools_used": null
}
```

### 3. Get Session Info

**GET** `/sessions/{session_id}`

Get information about a specific session.

```bash
curl http://localhost:8000/sessions/user123
```

### 4. List All Sessions

**GET** `/sessions`

List all active sessions.

```bash
curl http://localhost:8000/sessions
```

### 5. Delete Session

**DELETE** `/sessions/{session_id}`

Clear a session's chat history.

```bash
curl -X DELETE http://localhost:8000/sessions/user123
```

## Testing with Postman

### Setup

1. **Open Postman**
2. **Create a New Collection** named "AgentEasy Agent API"

### Test 1: Health Check

1. Create a new request: `GET http://localhost:8000/health`
2. Click **Send**
3. You should see status `200 OK`

### Test 2: Simple Greeting

1. Create a new request: `POST http://localhost:8000/chat`
2. Set **Headers**:
   - `Content-Type`: `application/json`
3. Set **Body** (raw JSON):
   ```json
   {
     "message": "Hello  AgentEasy! My name is John.",
     "session_id": "test-session-1"
   }
   ```
4. Click **Send**
5. You should get a greeting from AgentEasy

### Test 3: Math Calculation

1. Create a new request: `POST http://localhost:8000/chat`
2. Set **Body** (raw JSON):
   ```json
   {
     "message": "What is ((25 * 4) ^ 2)?",
     "session_id": "test-session-1"
   }
   ```
3. Click **Send**
4. AgentEasy will use the Calculator tool and return: "The result is 10000"

### Test 4: RAG - Ask About AgentEasy

1. Create a new request: `POST http://localhost:8000/chat`
2. Set **Body** (raw JSON):
   ```json
   {
     "message": "Where were you created?",
     "session_id": "test-session-1"
   }
   ```
3. Click **Send**
4. AgentEasy will use the RAG retriever and answer based on his dialogue history

### Test 5: Web Search (if Tavily is configured)

1. Create a new request: `POST http://localhost:8000/chat`
2. Set **Body** (raw JSON):
   ```json
   {
     "message": "What is the top news story today?",
     "session_id": "test-session-1"
   }
   ```
3. Click **Send**
4. AgentEasy will search the web and return current news

### Test 6: Memory Check

1. Use the same `test-session-1` session
2. Send:
   ```json
   {
     "message": "What is my name?",
     "session_id": "test-session-1"
   }
   ```
3. AgentEasy should remember you said "John" in Test 2

### Test 7: Check Session

1. Create a new request: `GET http://localhost:8000/sessions/test-session-1`
2. Click **Send**
3. You'll see how many messages are in the session

## Postman Collection Import

You can import this collection JSON into Postman:

```json
{
  "info": {
    "name": " AgentEasy Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Chat - Greeting",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"Hello  AgentEasy!\",\n  \"session_id\": \"test-session\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/chat",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["chat"]
        }
      }
    },
    {
      "name": "Chat - Math",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"What is ((2 * 8) ^ 2)?\",\n  \"session_id\": \"test-session\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/chat",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["chat"]
        }
      }
    },
    {
      "name": "Get Session Info",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/sessions/test-session",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["sessions", "test-session"]
        }
      }
    },
    {
      "name": "List All Sessions",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/sessions",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["sessions"]
        }
      }
    },
    {
      "name": "Delete Session",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/sessions/test-session",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["sessions", "test-session"]
        }
      }
    }
  ]
}
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found in environment variables"

**Solution**: Make sure you created a `.env` file with your API key.

### Issue: Agent initialization takes too long

**Solution**: First initialization can take 1-2 minutes as it:
- Loads all dialogue lines
- Creates embeddings
- Builds the vector AgentEasybase

Subsequent requests will be fast.

### Issue: "No dialogue lines found"

**Solution**: The API will use fallback AgentEasy. If you want real AgentEasy dialogue, add TNG scripts to `sample_AgentEasy/tng/`.

### Issue: Web search not working

**Solution**: Make sure you've added `TAVILY_API_KEY` to your `.env` file. Web search is optional.

### Issue: Port 8000 already in use

**Solution**: Change the port:
```bash
uvicorn main:app --reload --port 8001
```

## Architecture

```
┌─────────────┐
│   Client    │  (Postman, curl, etc.)
│  (HTTP)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  ┌──────────────────────────────┐   │
│  │     Session Management       │   │
│  │  (ChatMessageHistory per ID) │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │      Agent Executor          │   │
│  │  ┌────────────────────────┐  │   │
│  │  │   LangChain Agent      │  │   │
│  │  │   (OpenAI Functions)   │  │   │
│  │  └────────────────────────┘  │   │
│  │          │                    │   │
│  │    ┌─────┴─────┐             │   │
│  │    │   Tools   │             │   │
│  │    │           │             │   │
│  │    │ • RAG     │ Vector DB   │   │
│  │    │ • Math    │ Calculator  │   │
│  │    │ • Search  │ Tavily API  │   │
│  │    └───────────┘             │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

## License

This is an educational project based on the original notebook.

## Credits

- Based on the  AgentEasy Agent notebook
- Star Trek: The Next Generation scripts from ST-Minutiae.com
- Built with LangChain and FastAPI

