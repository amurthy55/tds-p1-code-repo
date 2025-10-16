# Script requires python 3.11 or above
# Dependencies=["python>=3.11","fastapi[standar]",uvicorn, openai,requests]

import os
import json
from fastapi import FastAPI, Request
import requests
import base64

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
app = FastAPI()


def validate_secret(secret: str) -> bool:
    # In a real application, replace this with secure validation
    return secret == os.getenv("secret")

def create_gihub_repo(repo_name: str):
    # Placeholder for GitHub repo creation logic using GitHub API with the token from env variable and the repo_name
    payload = {
               "name": repo_name, 
               "private": False,
               "auto_init": True,
               "license_template": "mit" 
               }
    headers = { "Authorization": f"Bearer {GITHUB_TOKEN}" }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Repository {repo_name} created successfully.")
        return response.json()
    else:
        print(f"Failed to create repository {repo_name}. Response: {response.json()}")
        raise Exception("GitHub repo creation failed")

def get_sha_of_latest_commit(repo_name: str, branch_name) -> str:
    # takes repo_name and branch name as input and returns the sha of the latest commit using github api
    headers = { "Authorization": f"Bearer {GITHUB_TOKEN}" }
    response = requests.get(f"https://api.github.com/repos/amurthy55/{repo_name}/branches/{branch_name}", headers=headers)
    if response.status_code == 200: 
        branch_info = response.json()
        return branch_info["commit"]["sha"] 
    else:
        print(f"Failed to get latest commit SHA for branch {branch_name} in repository {repo_name}. Response: {response.json()}")
        raise Exception("GitHub get latest commit SHA failed")
    
def push_files_to_repo(repo_name: str, files: list[dict], round: int = 1):
    # takes repo_name and json array of files(with fields file_name and content ) as input and pushes the files to the repo using github api 
    if(round == 2):
        latest_sha = get_sha_of_latest_commit(repo_name, "main")
    else:
        latest_sha = None

    headers = { "Authorization": f"Bearer {GITHUB_TOKEN}" }
    for file in files:    
        file_name = file['file_name']
        file_content = file['content']

        if isinstance(file_content, bytes):
            file_content = base64.b64encode(file_content).decode('utf-8')
        
        else:
            file_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        payload = { "message": f"Add {file_name}",
                    "content": file_content,
                    "branch": "main"
                  }
        if latest_sha:
            payload["sha"] = latest_sha

        response = requests.put(f"https://api.github.com/repos/amurthy55/{repo_name}/contents/{file_name}", headers=headers, json=payload)
        if response.status_code == 201:
            print(f"File {file['file_name']} pushed to repository {repo_name}.")
        else:
            print(f"Failed to push file {file['file_name']} to repository {repo_name}. Response: {response.json()}")
            raise Exception("GitHub push file failed")

def enable_github_pages(repo_name: str):
    # takes repo_name as input and enables github pages for that repo using github api
    headers = { "Authorization": f"Bearer {GITHUB_TOKEN}" }
    payload = { "build_type":"legacy",
                "source": { "branch": "main", "path": "/" } 
              }
    response = requests.post(f"https://api.github.com/repos/amurthy55/{repo_name}/pages", headers=headers, json=payload)
    if response.status_code == 201:
        print(f"GitHub Pages enabled for repository {repo_name}.")
    

def write_code_with_llm():
    #hard code with a single file for now
    # TODO: integrate with LLM to generate code based.
    return [ 
            { "file_name": "index.html", 
              "content": """
              <!DOCTYPE html>
<html>
  <head>
    <base target="_top">
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 30px;
        background: #f6f8fa;
      }
      h2 {
        color: #333;
      }
      select, button {
        font-size: 16px;
        padding: 8px;
        margin-top: 10px;
      }
      #status {
        margin-top: 20px;
        font-weight: bold;
      }
    </style>
  </head>
  <body>
    <h2>Coded by LLM</h2>
    <form id="emailForm" onsubmit="handleSubmit(event)">
      <select id="emailSelect" required>
        <option value="">--Select Email--</option>
        <option>user1@example.com</option>
        <option>user2@example.com</option>
        <option>user3@example.com</option>
        <option>user4@example.com</option>
        <option>user5@example.com</option>
        <option>user6@example.com</option>
        <option>user7@example.com</option>
        <option>user8@example.com</option>
        <option>user9@example.com</option>
        <option>user10@example.com</option>
      </select>
      <br>
      <button type="submit">Submit</button>
    </form>

    <div id="status"></div>

    <script>
      function handleSubmit(event) {
        event.preventDefault();
        const email = document.getElementById("emailSelect").value;
        document.getElementById("status").innerText = "Processing...";
        google.script.run
          .withSuccessHandler(msg => document.getElementById("status").innerText = msg)
          .processEmail(email);
      }
    </script>
  </body>
</html>
""",            }   
            ]

def round1(data):
    print("Executing Round 1 tasks...")
    # Placeholder for round 1 logic
    # e.g., setting up environment, initial checks, etc.
    new_repo_name = f'{data["task"]}_{data["nonce"]}'
    create_gihub_repo(new_repo_name)
    files = write_code_with_llm()
    push_files_to_repo(new_repo_name,files)
    enable_github_pages(new_repo_name)

   

def round2(data):
    print("Executing Round 2 tasks...")
    # Placeholder for round 2 logic
    # e.g., more advanced checks, evaluations, etc.
   


#post end point that takes json input with following fields : email, secret, task, round, nounce, brief, checks, evaluation_url,attachments
@app.post("/handle_task")
async def handle_task(request: Request):
    data = await request.json()
    print("Received data:", data)
    #validate the secret
    if not validate_secret(data.get("secret")):
        return {"status": "error", "message": "Invalid secret"}
    else:
        print(data)
        if data.get("round") == 1:
            round1(data)
            return {"status": "Finished", "message": "Round 1 tasks executed"}
        elif data.get("round") == 2:
            round2(data)
            return {"status": "Finished", "message": "Round 2 tasks executed"}
        else:
            return {"status": "error", "message": "Invalid round"}
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
