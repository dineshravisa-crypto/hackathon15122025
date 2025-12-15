# Windows Installation Guide - Manual Steps

If you're getting "Access is denied" errors, follow these manual steps:

## Step 1: Open Command Prompt as Administrator

1. Press `Windows Key`
2. Type "cmd"
3. **Right-click** "Command Prompt"
4. Select **"Run as administrator"**
5. Click "Yes" on the UAC prompt

## Step 2: Navigate to the API Directory

```cmd
cd E:\MLCourse\GenAI\api
```

## Step 3: Create Virtual Environment

```cmd
python -m venv venv
```

## Step 4: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

## Step 5: Upgrade Pip

```cmd
python -m pip install --upgrade pip
```

## Step 6: Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

This will take 2-3 minutes. You'll see packages being installed.

## Step 7: Verify Installation

```cmd
pip list
```

You should see `fastapi`, `uvicorn`, `langchain-openai`, etc.

## Step 8: Run the Server

```cmd
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Initializing Commander Data Agent...
```

## Step 9: Test in Browser

Open: http://localhost:8000/docs

You should see the API documentation!

## Alternative: Install Packages One by One

If pip installations keep failing, you can try installing packages individually:

```cmd
pip install fastapi
pip install uvicorn[standard]
pip install python-dotenv
pip install langchain-openai
pip install langchain-classic
pip install langchain-core
pip install langchain-community
pip install langchain-experimental
pip install openai
```

## Still Having Issues?

### Check Python Installation
```cmd
python --version
```
Should show Python 3.10 or higher

### Check if Python is in PATH
```cmd
where python
```
Should show path to python.exe

### Check Write Permissions
Try creating the venv in your user directory:
```cmd
cd %USERPROFILE%\Documents
mkdir data-agent-api
cd data-agent-api
```

Then copy your files there and try again.

## Quick Test Without Virtual Environment (Not Recommended)

If you absolutely cannot create a virtual environment:

```cmd
cd E:\MLCourse\GenAI\api
pip install -r requirements.txt --user
python main.py
```

⚠️ **Warning**: The `--user` flag installs packages globally in your user directory, which can cause conflicts with other projects. Use virtual environments when possible.

## Need More Help?

Common issues:

1. **Antivirus blocking**: Temporarily disable Windows Defender
2. **Corporate network**: May need to configure proxy for pip
3. **Old Python**: Upgrade to Python 3.10+
4. **Corrupted pip**: Reinstall Python

If you're on a corporate/restricted computer, you may need IT administrator help.

