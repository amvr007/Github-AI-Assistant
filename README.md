# GitHub AI Agent

An AI agent that analyzes GitHub repositories using MCP architecture.

## Setup

1. **Install dependencies**
   ```bash
   pip install streamlit langchain langchain-ollama langgraph langchain-mcp-adapters mcp fastmcp requests

1. **Install ollama and pull model**
   ```bash
   ollama pull llama3.2:3b

## Usage

### Web Interface:
   ```bash
   streamlit run app.py
   ```

### Command Line:
```bash
   python agent.py
   ```


## Features:
* Analyze repositories
* Search for projects
* Read file contents
* Conversation memory

