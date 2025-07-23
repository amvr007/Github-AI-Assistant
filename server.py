from mcp.server.fastmcp import FastMCP 
import requests

server = FastMCP("github-server")


@server.prompt()
async def system_prompt() -> str: 
    """System prompt decription"""
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: system_prompt.txt file not found. Please create this file in the server directory."
    except Exception as e:
        return f"Error reading system prompt file: {str(e)}"


@server.tool()
async def get_repo_info(owner: str, repo: str) -> str:
    """a function that gets Github repository information"""
    url = f"https://api.github.com/repos/{owner}/{repo}"

    try: 
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            result = f"the owner's name is:  {data['full_name']} \n"
            result += f"Description: {data['description'] or 'no description'} \n" 
            result += f"Created: {data['created_at'][:10]}\n"
            result += f"URL: {data['html_url']} \n"

            return result
        
        else: 
            return f"repository not found: {response.status_code}"
        
    except Exception as e: 
        return f'Error: {str(e)}'



@server.tool()
async def search_repos(query: str) -> str:
    """a function that searches for repositories based on a query"""
    limit = 10
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={limit}"

    try: 
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            result =  f"These are the repositories found based on  your Query\n"
            result += f"query: {query} \n"

            for i,repo in enumerate(data["items"], 1):
                result += f"{i}.{repo['full_name']}\n"
                result += f"Language: {repo['language']} \n"
                result += f"Description: {repo['description']} \n"

            return result
        
        else:
            return f"no repository found {response.status_code}"
    
    except Exception as e: 
        return f"Error: {str(e)}"
    



@server.tool()
async def get_file_content(owner: str, repo: str, path: str) -> str:
    "a function that gets content of a specific file in a github repository"
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    try: 
        response = requests.get(url)

        if response.status_code == 200: 
            data = response.json()

            if data['type'] == 'file': 
                import base64

                content = base64.b64decode(data['content']).decode('utf-8')

                result = f" {data['name']}  from {owner}/{repo}\n"
                result += f"Content: \n  ```\n{content}\n```"

                return result
            else:
               return f"{path} is a directory, not a file"
        else:
            return f"File not found: {response.status_code}"
           
    except Exception as e:
       return f" Error: {str(e)}" 



if __name__ == "__main__":
    server.run()

    
