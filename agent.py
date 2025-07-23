from typing import List, Annotated
from typing_extensions import TypedDict

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio



async def create_graph(session):
    llm = ChatOllama(model="llama3.2:3b", temperature=0)

    tools = await load_mcp_tools(session)
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = await load_mcp_prompt(session, name= "system_prompt")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt[0].content),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools


    class State(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]


    def chat_node(state: State) -> State:
        response = chat_llm.invoke({"messages": state["messages"]})
        return {"messages": [response]}


    graph_builder = StateGraph(State)

    graph_builder.add_node("chat_node", chat_node)
    graph_builder.add_node("tool_node", ToolNode(tools=tools))

    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
    graph_builder.add_edge("tool_node", "chat_node")

    graph = graph_builder.compile(checkpointer=MemorySaver())

    return graph 


server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env=None,
)


async def main(): 
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            agent = await create_graph(session)
            config = {"configurable": {"thread_id": "1"}}
            
            while True: 
                message = input("User: ")
                if message.lower() in ['quit', 'exit']:
                    break
                    
                response = await agent.ainvoke(
                    {"messages": [HumanMessage(content=message)]}, 
                    config
                )
                print("Agent: " + response["messages"][-1].content)



if __name__ == "__main__":
    asyncio.run(main())