import asyncio
import os 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env=os.environ.copy(),
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write)  as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            print("\n=== Repository Info ===")
            result = await session.call_tool("get_repo_info", 
                arguments={"owner": "microsoft", "repo": "vscode"})
            print(result.content[0].text)

            print("\n=== Search Repos ===")
            result = await session.call_tool("search_repos", 
                arguments={"query": "python web framework"})
            print(result.content[0].text)

            print("\n=== File Content ===")
            result = await session.call_tool("get_file_content", 
                arguments={
                    "owner": "octocat", 
                    "repo": "Hello-World", 
                    "path": "README"
                })
            print(result.content[0].text)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()


