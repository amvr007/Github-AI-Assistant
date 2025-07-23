import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage
from agent import create_graph, server_params
from mcp import ClientSession
from mcp.client.stdio import stdio_client

st.title("🐙 GitHub AI Agent")

# Initialize session state for conversation
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "github_session"}}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about any GitHub repository..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with agent
    async def get_response():
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                graph = await create_graph(session)
                
                if st.session_state.conversation_state is None:
                    # First message
                    initial_state = {
                        "messages": [HumanMessage(content=prompt)]
                    }
                    st.session_state.conversation_state = initial_state
                else:
                    # Continue conversation
                    st.session_state.conversation_state["messages"].append(HumanMessage(content=prompt))
                
                # Get agent response
                result = graph.invoke(
                    st.session_state.conversation_state,
                    st.session_state.config
                )
                return result
    
    # Get agent response
    try:
        with st.spinner("🤖 Analyzing GitHub data..."):
            result = asyncio.run(get_response())
            response = result["messages"][-1].content
            
            # Update conversation state
            st.session_state.conversation_state = result
            
            # Add agent response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
                
            # Debug info in sidebar
            with st.sidebar:
                st.header("Debug Info")
                st.write(f"Messages in conversation: {len(result.get('messages', []))}")
                st.write(f"Total chat messages: {len(st.session_state.messages)}")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Debug: Check your agent.py and server.py files")

# Sidebar with examples
with st.sidebar:
    st.header("💡 Examples")
    
    examples = [
        "Analyze microsoft/vscode",
        "Find Python web frameworks", 
        "Show README of facebook/react"
    ]
    
    for example in examples:
        if st.button(example, key=f"ex_{example}"):
            st.session_state.messages.append({"role": "user", "content": example})
            st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.conversation_state = None
        st.session_state.messages = []
        st.rerun()