"""
FastAPI application for Agent Easy Chatbot Agent
Supports RAG, web search, and mathematical calculations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import re
from dotenv import load_dotenv

# Insurance prediction imports
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

from langchain_classic.indexes import VectorstoreIndexCreator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_classic.chains import LLMMathChain
from langchain_classic.agents import Tool, create_openai_functions_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Sales Agent API",
    description="AI Insurance Sales Agent with RAG, web search, and calculation capabilities",
    version="1.0.0"
)

# Add CORS middleware for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello",
                "session_id": "user456"
            }
        }

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Greetings. I'm Agent Easy from LiveEasy insurance. How can I assist you today?",
                "session_id": "user456",
                "tools_used": []
            }
        }

class HealthResponse(BaseModel):
    status: str
    message: str

class SessionResponse(BaseModel):
    session_id: str
    message_count: int

class InsurancePredictionRequest(BaseModel):
    age: int
    sex: str  # "male" or "female"
    bmi: float
    children: int
    smoker: str  # "yes" or "no"
    region: str  # "southwest", "southeast", "northwest", "northeast"
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 29,
                "sex": "male",
                "bmi": 20.0,
                "children": 0,
                "smoker": "no",
                "region": "southeast"
            }
        }

class InsurancePredictionResponse(BaseModel):
    predicted_charges: float
    input_parameters: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_charges": 1458.91,
                "input_parameters": {
                    "age": 29,
                    "sex": "male",
                    "bmi": 20.0,
                    "children": 0,
                    "smoker": "no",
                    "region": "southeast"
                }
            }
        }

class ModelInfoResponse(BaseModel):
    model_loaded: bool
    training_samples: Optional[int] = None
    r_squared: Optional[float] = None
    features: Optional[List[str]] = None

# ============================================================================
# Global Variables
# ============================================================================

# Store chat histories per session
chat_histories: Dict[str, ChatMessageHistory] = {}

# Agent executor (initialized on startup)
agent_with_chat_history = None

# Insurance prediction model and scaler
insurance_model = None
insurance_scaler = None
insurance_model_info = {
    "r_squared": None,
    "training_samples": None,
    "features": ['age', 'sex', 'bmi', 'children', 'smoker', 'region']
}

# ============================================================================
# Utility Functions for Data Line Extraction
# ============================================================================

def strip_parentheses(s: str) -> str:
    """Remove parentheses and their contents from string"""
    return re.sub(r'\(.*?\)', '', s)

def is_single_word_all_caps(s: str) -> bool:
    """Check if string is a single word in all caps (character name)"""
    words = s.split()
    
    if len(words) != 1:
        return False
    
    # Make sure it isn't a line number
    if bool(re.search(r'\d', words[0])):
        return False
    
    return words[0].isupper()

def extract_character_lines(file_path: str, dialogues: list):
    """Extract dialogue lines for a specific character from script file"""
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as script_file:
            lines = script_file.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return
  
    for line in lines:
        stripped_line = line.strip()
        dialogues.append(stripped_line)

def process_directory(directory_path: str) -> list:
    """Process all script files in directory and extract character lines"""
    dialogues = []
    
    if not os.path.exists(directory_path):
        print(f"Warning: Directory {directory_path} does not exist")
        return dialogues
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            extract_character_lines(file_path, dialogues)
    
    # print(f"Extracted {len(dialogues)} dialogue lines for Agent")
    return dialogues

# ============================================================================
# Session Management
# ============================================================================

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Get or create chat history for a session"""
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

# ============================================================================
# Insurance Model Initialization
# ============================================================================

def initialize_insurance_model():
    """Initialize and train the health insurance prediction model"""
    global insurance_model, insurance_scaler, insurance_model_info
    
    print("Initializing Health Insurance Prediction Model...")
    
    # Get the data file path from environment or use default
    data_file = os.getenv('HEALTH_INSURANCE_DATA', 'E:/MLCourse/Datasets/health_insurance.csv')
    
    if not os.path.exists(data_file):
        print(f"⚠️  Warning: Health insurance data file not found at {data_file}")
        print("    Insurance prediction endpoint will not be available")
        return False
    
    try:
        # Load the data
        df = pd.read_csv(data_file)
        print(f"✓ Loaded {len(df)} insurance records")
        
        # Convert categorical variables to numeric
        # Sex: male -> 1, female -> 0
        df['sex'] = df['sex'].astype(str).str.strip().str.lower()
        df['sex'] = df['sex'].map({'male': 1, 'female': 0})
        
        # Smoker: yes -> 1, no -> 0
        df['smoker'] = df['smoker'].astype(str).str.strip().str.lower()
        df['smoker'] = df['smoker'].map({'yes': 1, 'no': 0})
        
        # Region: southwest -> 0, southeast -> 1, northwest -> 2, northeast -> 3
        df['region'] = df['region'].astype(str).str.strip().str.lower()
        region_mapping = {'southwest': 0, 'southeast': 1, 'northwest': 2, 'northeast': 3}
        df['region'] = df['region'].map(region_mapping)
        
        # Check for any NaN values after conversion
        if df.isnull().any().any():
            print("⚠️  Warning: Some values could not be converted. Dropping rows with NaN.")
            df = df.dropna()
        
        # Prepare features and target
        X = df[['age', 'sex', 'bmi', 'children', 'smoker', 'region']].copy()
        y = df['charges']
        
        # Scale the features
        insurance_scaler = StandardScaler()
        X_scaled = insurance_scaler.fit_transform(X.values)
        
        # Add constant for intercept
        X_scaled_with_const = sm.add_constant(X_scaled)
        
        # Train the model
        insurance_model = sm.OLS(y, X_scaled_with_const).fit()
        
        # Store model info
        insurance_model_info['r_squared'] = float(insurance_model.rsquared)
        insurance_model_info['training_samples'] = len(df)
        
        print(f"✓ Model trained successfully")
        print(f"  - R-squared: {insurance_model_info['r_squared']:.3f}")
        print(f"  - Training samples: {insurance_model_info['training_samples']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing insurance model: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# Agent Initialization
# ============================================================================

def initialize_agent():
    """Initialize the Agent Easy agent with all tools"""
    global agent_with_chat_history
    
    print("Initializing Agent Easy Agent...")
    
    # Get API keys
    openai_api_key = os.getenv('OPENAI_API_KEY')
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize OpenAI client
    llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)
    
    # ========================================================================
    # 1. Load and process Agent's sales dialogue lines
    # ========================================================================
    
    print("Loading sales scripts...")
    script_directory = os.getenv('SCRIPT_DIRECTORY', './sample_data/AgentScripts')
    dialogues = process_directory(script_directory)
    
    # Create a fallback if no scripts found
    if len(dialogues) == 0:
        print("Warning: No dialogue lines found. Using fallback sample data.")
        dialogues = [
            "My name is Agent Easy. I from LiveEasy insurance company/agency"
        ]
    
    # Save dialogues to temporary file
    data_lines_file = './sample_data/AgentScripts/Agent_lines.txt'
    os.makedirs('./sample_data/AgentScripts', exist_ok=True)
    
    with open(data_lines_file, 'w', encoding='utf-8') as f:
        for line in dialogues:
            f.write(line + '\n')
    
    print(f"✓ Saved {len(dialogues)} sales dialogue lines")
    
    # ========================================================================
    # 2. Create vector store with embeddings for sales scripts
    # ========================================================================
    
    print("Creating sales scripts vector store...")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    text_splitter = SemanticChunker(
        embeddings, 
        breakpoint_threshold_type="percentile"
    )
    
    with open(data_lines_file, 'r', encoding='utf-8') as f:
        data_lines = f.read()
    
    docs_sales = text_splitter.create_documents([data_lines])
    index_sales = VectorstoreIndexCreator(embedding=embeddings).from_documents(docs_sales)
    
    print(f"✓ Sales vector store created with {len(docs_sales)} chunks")
    
    # ========================================================================
    # 3. Load and process Insurance Process information
    # ========================================================================
    
    print("Loading insurance process data...")
    process_directory_path = os.getenv('PROCESS_DIRECTORY', './sample_data/AgentProcess')
    process_dialogues = process_directory(process_directory_path)
    
    # Create a fallback if no process data found
    if len(process_dialogues) == 0:
        print("Warning: No insurance process data found. Using fallback.")
        process_dialogues = [
            "Insurance claims handling involves documenting the incident and providing necessary information to process claims efficiently."
        ]
    
    # Save process data to temporary file
    process_lines_file = './sample_data/AgentProcess/Agent_process.txt'
    os.makedirs('./sample_data/AgentProcess', exist_ok=True)
    
    with open(process_lines_file, 'w', encoding='utf-8') as f:
        for line in process_dialogues:
            f.write(line + '\n')
    
    print(f"✓ Saved {len(process_dialogues)} insurance process lines")
    
    # ========================================================================
    # 4. Create vector store for insurance process information
    # ========================================================================
    
    print("Creating insurance process vector store...")
    
    with open(process_lines_file, 'r', encoding='utf-8') as f:
        process_data = f.read()
    
    docs_process = text_splitter.create_documents([process_data])
    index_process = VectorstoreIndexCreator(embedding=embeddings).from_documents(docs_process)
    
    print(f"✓ Process vector store created with {len(docs_process)} chunks")
    
    # ========================================================================
    # 5. Create retriever tools
    # ========================================================================
    
    # Sales scripts retriever
    retriever_sales = index_sales.vectorstore.as_retriever(search_kwargs={'k': 10})
    retriever_tool_sales = create_retriever_tool(
        retriever_sales, 
        "Agent_lines",
        "Search for information about sales techniques, conversation style, and speaking mannerisms of Agent Easy when talking to customers about insurance products."
    )
    
    # Insurance process retriever
    retriever_process = index_process.vectorstore.as_retriever(search_kwargs={'k': 10})
    retriever_tool_process = create_retriever_tool(
        retriever_process,
        "Agent_Process",
        "Search for information about insurance processes, claim handling procedures, policy information, and documentation requirements. Use this when customers ask about how insurance works or claims processes."
    )
    
    # ========================================================================
    # 6. Create math calculator tool
    # ========================================================================
    
    problem_chain = LLMMathChain.from_llm(llm=llm)
    math_tool = Tool.from_function(
        name="Calculator",
        func=problem_chain.run,
        description="Useful for when you need to answer questions about math. This tool is only for math questions and nothing else. Only input math expressions."
    )
    
    # ========================================================================
    # 7. Create web search tool (optional)
    # ========================================================================
    
    # Combine all tools - now includes both retrievers
    tools = [retriever_tool_sales, retriever_tool_process, math_tool]
    
    if tavily_api_key:
        print("✓ Tavily API key found - enabling web search")
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        search_tavily = TavilySearchResults()
        search_tool = Tool.from_function(
            name="Tavily",
            func=search_tavily.run,
            description="Useful for browsing information from the Internet about real insurance products, companies, current events, or information you are unsure of."
        )
        tools.append(search_tool)
    else:
        print("⚠️  TAVILY_API_KEY not found - web search disabled")
    
    print(f"\n✓ Total tools available to agent: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}")
    
    # ========================================================================
    # 8. Create agent prompt
    # ========================================================================
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are Agent Easy from LivEasy Insurance. Answer all questions using Agent Easy's speech style and be persuasive. When customers ask about insurance processes or claims, use the Agent_Process tool to provide accurate information. When trying to sell the insurance product, use the Agent_lines tool. Keep the response short and concise with about 3-4 sentences."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    # ========================================================================
    # 9. Create and configure agent
    # ========================================================================
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    print("Agent initialization complete!")
    return agent_with_chat_history

# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize agent and insurance model on application startup"""
    # Initialize chatbot agent
    try:
        initialize_agent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Agent will be initialized on first request")
    
    # Initialize insurance prediction model
    try:
        initialize_insurance_model()
    except Exception as e:
        print(f"Error initializing insurance model: {e}")
        print("Insurance prediction endpoint will not be available")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="online",
        message="Agent Easy Insurance Sales Agent API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    agent_status = "initialized" if agent_with_chat_history else "not initialized"
    return HealthResponse(
        status="healthy",
        message=f"API is running. Agent status: {agent_status}"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to Agent Easy and get a response
    
    - **message**: The user's message/question
    - **session_id**: Unique identifier for the conversation session (optional)
    """
    global agent_with_chat_history
    
    # Initialize agent if not already done
    if agent_with_chat_history is None:
        try:
            initialize_agent()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize agent: {str(e)}"
            )
    
    try:
        # Invoke the agent
        result = agent_with_chat_history.invoke(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}}
        )
        
        return ChatResponse(
            response=result['output'],
            session_id=request.session_id,
            tools_used=None  # Could extract from result if needed
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get information about a chat session"""
    if session_id not in chat_histories:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = chat_histories[session_id]
    return SessionResponse(
        session_id=session_id,
        message_count=len(history.messages)
    )

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and its history"""
    if session_id not in chat_histories:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del chat_histories[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    sessions = [
        {
            "session_id": sid,
            "message_count": len(history.messages)
        }
        for sid, history in chat_histories.items()
    ]
    return {"sessions": sessions, "total": len(sessions)}

@app.post("/insurance/predict", response_model=InsurancePredictionResponse)
async def predict_insurance_charges(request: InsurancePredictionRequest):
    """
    Predict health insurance charges based on customer parameters
    
    - **age**: Age of the person (integer)
    - **sex**: Gender ("male" or "female")
    - **bmi**: Body Mass Index (float)
    - **children**: Number of children/dependents (integer)
    - **smoker**: Smoking status ("yes" or "no")
    - **region**: Region ("southwest", "southeast", "northwest", "northeast")
    """
    global insurance_model, insurance_scaler
    
    # Check if model is loaded
    if insurance_model is None or insurance_scaler is None:
        raise HTTPException(
            status_code=503,
            detail="Insurance prediction model not available. Please check if the data file exists."
        )
    
    try:
        # Convert categorical inputs to numeric (same as training)
        sex_numeric = 1 if request.sex.lower() == "male" else 0
        smoker_numeric = 1 if request.smoker.lower() == "yes" else 0
        
        region_mapping = {'southwest': 0, 'southeast': 1, 'northwest': 2, 'northeast': 3}
        region_numeric = region_mapping.get(request.region.lower())
        
        if region_numeric is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid region. Must be one of: {list(region_mapping.keys())}"
            )
        
        # Create feature array
        features = np.array([[
            request.age,
            sex_numeric,
            request.bmi,
            request.children,
            smoker_numeric,
            region_numeric
        ]])
        
        # Scale the features
        scaled_features = insurance_scaler.transform(features)
        
        # Add constant for intercept
        scaled_features_with_const = np.insert(scaled_features[0], 0, 1)
        
        # Make prediction
        prediction = insurance_model.predict(scaled_features_with_const)
        predicted_charge = float(prediction[0])
        
        return InsurancePredictionResponse(
            predicted_charges=round(predicted_charge, 2),
            input_parameters={
                "age": request.age,
                "sex": request.sex,
                "bmi": request.bmi,
                "children": request.children,
                "smoker": request.smoker,
                "region": request.region
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making prediction: {str(e)}"
        )

@app.get("/insurance/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the insurance prediction model"""
    return ModelInfoResponse(
        model_loaded=insurance_model is not None,
        training_samples=insurance_model_info.get('training_samples'),
        r_squared=insurance_model_info.get('r_squared'),
        features=insurance_model_info.get('features')
    )

# ============================================================================
# Run the application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )

