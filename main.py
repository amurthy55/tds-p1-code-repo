# Script requires python 3.11 or above
# Dependencies=["python>=3.11","fastapi[standar]",uvicorn, openai,requests]

import os
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import base64
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "amurthy55"
app = FastAPI()


def validate_secret(secret: str) -> bool:
    print(secret)
    # In a real application, replace this with secure validation
    return secret == os.getenv("secret")

def create_gihub_repo(repo_name: str):
    print(GITHUB_TOKEN)
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
 

# def push_files_to_repo(repo_name: str, files: list[dict]):
#     headers = {
#         "Authorization": f"token {GITHUB_TOKEN}",
#         "Accept": "application/vnd.github.v3+json"
#     }

#     for f in files:
#         file_name = f["file_name"]
#         content_b64 = base64.b64encode(f["content"].encode()).decode()

#         # ✅ Check if the file already exists
#         get_url = f"https://api.github.com/repos/amurthy55/{repo_name}/contents/{file_name}"
#         get_resp = requests.get(get_url, headers=headers)

#         sha = None
#         if get_resp.status_code == 200:
#             sha = get_resp.json().get("sha")

#         data = {
#             "message": f"Add or update {file_name}",
#             "content": content_b64,
#         }
#         if sha:
#             data["sha"] = sha  # Required for updating existing file

#         put_url = f"https://api.github.com/repos/amurthy55/{repo_name}/contents/{file_name}"
#         put_resp = requests.put(put_url, headers=headers, json=data)

#         if put_resp.status_code not in [200, 201]:
#             print(f"⚠️ Failed to push file {file_name}: {put_resp.json()}")
#             raise Exception("GitHub push file failed")

#     print(f"✅ All files pushed to {repo_name}")




def push_files_to_repo(repo_name, files, branch="main", retries=5, delay=2):
    """
    Push multiple files to GitHub repo. Handles new files and updates.
    Retries GET for new repos/files to avoid 404 due to propagation delay.
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    for file in files:
        path = file["file_name"]
        content_b64 = base64.b64encode(file["content"].encode()).decode()
        url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/{path}"

        # Retry GET to check if file exists
        sha = None
        for attempt in range(retries):
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                sha = resp.json().get("sha")
                break
            elif resp.status_code == 404:
                time.sleep(delay)  # wait and retry
            else:
                print(f"⚠️ GET {path} failed: {resp.json()}")
                break

        data = {"message": f"Add/update {path}", "content": content_b64, "branch": branch}
        if sha:
            data["sha"] = sha  # include SHA for update

        put_resp = requests.put(url, headers=headers, json=data)
        if put_resp.status_code in [200, 201]:
            print(f"✅ Pushed {path}")
        else:
            print(f"⚠️ Failed to push {path}: {put_resp.json()}")



def enable_github_pages(repo_name: str):
    # takes repo_name as input and enables github pages for that repo using github api
    headers = { "Authorization": f"Bearer {GITHUB_TOKEN}" }
    payload = { "build_type":"legacy",
                "source": { "branch": "main", "path": "/" } 
              }
    response = requests.post(f"https://api.github.com/repos/amurthy55/{repo_name}/pages", headers=headers, json=payload)
    if response.status_code == 201:
        print(f"GitHub Pages enabled for repository {repo_name}.")
    

# def write_code_with_llm(data):
#     """
#     Uses AI Pipe LLM API to generate minimal app code and README.md
#     based on the given 'brief' and 'attachments' in data.
#     Returns a list of file dicts [{file_name, content}, ...].
#     """

#     api_key = os.getenv("AIPIPE_API_KEY")
#     if not api_key:
#         raise Exception("Missing AIPIPE_API_KEY")

#     brief = data.get("brief", "")
#     attachments = data.get("attachments", [])

#     attachment_summary = ""
#     if attachments:
#         for att in attachments:
#             attachment_summary += f"- {att['name']}: {att.get('url','')[:100]}...\n"

#     prompt = f"""
#     You are an expert software engineer.
#     Based on the following task brief, generate a minimal runnable web app that fulfills the description.
#     --- TASK BRIEF ---
#     {brief}
#     --- ATTACHMENTS ---
#     {attachment_summary}
#     Requirements:
#     - Generate only valid UTF-8 text.
#     - Provide *only* JSON like this:
#       {{
#         "files": [
#           {{"file_name": "main.py", "content": "<code>"}},
#           {{"file_name": "README.md", "content": "<markdown>"}}
#         ]
#       }}
#     - Do not include any extra explanation or formatting outside the JSON.
#     """

#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {"role": "system", "content": "You are an expert code generator. Respond ONLY with valid JSON."},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.3
#     }

#     url = "https://aipipe.org/openrouter/v1/chat/completions"
#     response = requests.post(url, headers=headers, json=payload)

#     if response.status_code != 200:
#         print("AI Pipe error:", response.text)
#         raise Exception("AI Pipe LLM call failed")

#     result = response.json()
#     content = result["choices"][0]["message"]["content"].strip()

#     # 🔍 Parse nested JSON cleanly
#     try:
#         parsed = json.loads(content)
#         files = parsed.get("files", [])
#     except Exception:
#         # Some models double-encode JSON, e.g. as a string within another JSON
#         try:
#             inner = json.loads(json.loads(content))
#             files = inner.get("files", [])
#         except Exception as e:
#             print("⚠️ Could not parse LLM response, fallback to single file:", e)
#             files = [{"file_name": "main.py", "content": content}]

#     # 🚫 Strip accidental JSON wrapping (case you saw)
#     for f in files:
#         c = f["content"].strip()
#         if c.startswith("{") and '"files"' in c:
#             try:
#                 inner_json = json.loads(c)
#                 f["content"] = inner_json["files"][0]["content"]
#             except Exception:
#                 pass

#     return files

def write_code_with_llm(data, previous_files=None):
    """
    Generates or updates files using AI Pipe LLM API.

    - data: dict containing 'brief', 'attachments', 'checks', etc.
    - previous_files: list of dicts [{'file_name': ..., 'content': ...}] from round1,
                      used in round2 to update existing files.

    Returns a list of file dicts: [{'file_name': ..., 'content': ...}, ...]
    """

    api_key = os.getenv("AIPIPE_API_KEY")
    if not api_key:
        raise Exception("Missing AIPIPE_API_KEY")

    brief = data.get("brief", "")
    attachments = data.get("attachments", [])
    checks = data.get("checks", [])

       # --- Summarize attachments safely ---
    attachment_summary = ""
    if attachments:
      summary_lines = []
      for a in attachments:
          name = a.get("name", "unnamed")
          url = a.get("url", "")
          kind = "Unknown"
          snippet = ""

          if not isinstance(url, str):
              summary_lines.append(f"- {name} [Invalid URL format]")
              continue

          # Detect attachment kind
          if url.startswith("data:application/json;base64,"):
              kind = "JSON"
          elif url.startswith("data:text/csv;base64,"):
              kind = "CSV"
          elif url.startswith("data:text/markdown;base64,"):
              kind = "Markdown"
          elif url.startswith("data:text/plain;base64,"):
              kind = "Text"
          elif url.startswith("data:image/"):
              kind = "Image (base64)"
          elif url.startswith("http"):
              kind = "URL"

          # Attempt to decode text-like base64 data
          if "base64," in url and kind in ["JSON", "CSV", "Markdown", "Text"]:
              try:
                  b64data = url.split("base64,", 1)[1]
                  decoded = base64.b64decode(b64data).decode("utf-8", errors="ignore")
                  short_content = decoded[:800].replace("\n", "\\n")
                  snippet = f"[{kind} content snippet]: {short_content}..."
              except Exception as e:
                  snippet = f"[{kind} decoding failed: {e}]"
          else:
              # For images or non-decodable data
              short_url = (url[:100] + "...") if len(url) > 100 else url
              snippet = f"[{kind}]: {short_url}"

          summary_lines.append(f"- {name} {snippet}")

      attachment_summary = "\n".join(summary_lines)
    else:
          attachment_summary = "(No attachments provided)"

    # Summarize previous files for round2 context
    prev_files_summary = ""
    if previous_files:
        for f in previous_files:
            snippet = f['content'][:500].replace("\n", "\\n")
            prev_files_summary += f"- {f['file_name']} (content snippet): {snippet}...\n"

    # Summarize checks, handle both string and dict formats
    checks_summary = ""
    for c in checks:
        if isinstance(c, dict):
            brief_text = c.get("brief", "")
            js_checks = "\n".join([jc.get("js","") for jc in c.get("checks", [])])
            checks_summary += f"---\n{brief_text}\nChecks:\n{js_checks}\n"
        elif isinstance(c, str):
            checks_summary += f"- {c}\n"

    # Construct prompt differently for round1 vs round2
    if previous_files:
        # Round 2: update existing files
        prompt = f"""
You are an expert software engineer. You have the following existing files:
{prev_files_summary}

Task Brief:
{brief}

Checks / Evaluation Criteria:
{checks_summary}

--- ATTACHMENTS ---
{attachment_summary}

Update or modify the existing files to satisfy the brief and checks.
Preserve existing logic unless changes are required.
Always generate a README.md with summary, setup, usage, code explanation, license and description of the app

Provide ONLY JSON like this:
{{
  "files": [
    {{"file_name": "<name>", "content": "<updated content>"}}
  ]
}}
"""
    else:
        # Round 1: generate from scratch
        prompt = f"""
You are an expert software engineer.
Based on the following task brief, generate a minimal runnable app that fulfills the description.

Requirements:
- Generate at least one runnable app file (e.g., main.py, index.html)
- Always generate a README.md with summary, setup, usage, code explanation, license and description of the app
- Provide ONLY JSON with 'files' array, each element having 'file_name' and 'content'


--- TASK BRIEF ---
{brief}

--- ATTACHMENTS ---
{attachment_summary}

Checks / Evaluation Criteria:
{checks_summary}

Requirements:
- Generate only valid UTF-8 text.
- Provide ONLY JSON like this:
  {{
    "files": [
      {{"file_name": "<name>", "content": "<code/markdown/html>"}}
    ]
  }}
- Do not include any extra explanation or formatting outside the JSON.
"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an expert code generator. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    url = "https://aipipe.org/openrouter/v1/chat/completions"
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print("AI Pipe error:", resp.text)
        raise Exception("AI Pipe LLM call failed")

    content = resp.json()["choices"][0]["message"]["content"].strip()

    # Parse JSON robustly
    files = []
    try:
        parsed = json.loads(content)
        files = parsed.get("files", [])
    except Exception:
        try:
            inner = json.loads(json.loads(content))
            files = inner.get("files", [])
        except Exception as e:
            print("⚠️ Could not parse LLM response, fallback to single file:", e)
            files = [{"file_name": "main.py", "content": content}]

    # Remove accidental nested JSON wrapping in file content
    for f in files:
        c = f["content"].strip()
        if c.startswith("{") and '"files"' in c:
            try:
                inner_json = json.loads(c)
                f["content"] = inner_json["files"][0]["content"]
            except Exception:
                pass
    print(files)

    return files

def post_evaluation_result(data, repo_name):
    """Posts repo info to the evaluation URL with exponential backoff."""
    headers = {"Content-Type": "application/json"}

    # Compose payload
    repo_url = f"https://github.com/amurthy55/{repo_name}"
    pages_url = f"https://amurthy55.github.io/{repo_name}/"
    commit_sha = get_sha_of_latest_commit(repo_name, "main")

    payload = {
        "email": data["email"],
        "task": data["task"],
        "round": data["round"],
        "nonce": data["nonce"],
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url,
    }

    evaluation_url = data.get("evaluation_url")
    
    #MY OWN EVALUATION URL FOR TESTING
    # evaluation_url = "http://localhost:9000/notify"
    if not evaluation_url:
        print("No evaluation_url found in data.")
        return

    delay = 1  # seconds
    max_wait = 600  # 10 minutes
    start_time = time.time()

    while True:
        try:
            response = requests.post(evaluation_url, headers=headers, json=payload)
            if response.status_code == 200:
                print("✅ Evaluation URL accepted payload.")
                break
            else:
                print(f"⚠️  Evaluation post failed: {response.status_code}, retrying in {delay}s")
        except Exception as e:
            print(f"❌ Error posting to evaluation_url: {e}")

        # Stop after 10 minutes total
        if time.time() - start_time > max_wait:
            print("⏰ Gave up after 10 minutes without success.")
            break

        time.sleep(delay)
        delay = min(delay * 2, 60)  # backoff, capped at 60 s



def round1(data):
    print("Executing Round 1 tasks...")
    new_repo_name = f'{data["task"]}_{data["nonce"]}'

    # 1. Create repo with MIT license
    create_gihub_repo(new_repo_name)

    # 2. Generate minimal app with LLM
    files = write_code_with_llm(data)

    # 3. Push generated files
    push_files_to_repo(new_repo_name, files)

    # 4. Enable GitHub Pages
    enable_github_pages(new_repo_name)

    # 5. Notify evaluation_url with retries
    post_evaluation_result(data, new_repo_name)
   

# def round2(data):
#     print("Executing Round 2 tasks...")

#     repo_name = f'{data["task"]}_{data["nonce"]}'

#     # 1. Generate updated code/README based on new brief
#     files = write_code_with_llm(data)

#     # 2. Push updated files (handles existing files automatically)
#     push_files_to_repo(repo_name, files)

#     # 3. Optionally ensure Pages still enabled
#     # enable_github_pages(repo_name)

#     # 4. Notify evaluation URL with round=2
#     post_evaluation_result(data, repo_name)

def round2(data):
    print("Executing Round 2 tasks...")

    repo_name = f'{data["task"]}_{data["nonce"]}'

    # 1. Fetch all existing files in the repo
    current_files = []
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    resp = requests.get(url, headers=headers)
    print(f"Round 2 Response is : {resp.text}")
    if resp.status_code == 200:
        for item in resp.json():
            if item["type"] == "file":
                file_resp = requests.get(item["download_url"])
                if file_resp.status_code == 200:
                    current_files.append({
                        "file_name": item["name"],
                        "content": file_resp.text
                    })
                else:
                    print(f"⚠️ Could not fetch content of {item['name']}")
    else:
        print(f"⚠️ Could not list files in repo {repo_name}: {resp.json()}")

    # 2. Generate updated code/README based on new brief and previous files
    files = write_code_with_llm(data, previous_files=current_files)

    # 3. Push updated files (handles existing files automatically)
    push_files_to_repo(repo_name, files)

    # 4. Optionally ensure Pages still enabled
    # enable_github_pages(repo_name)

    # 5. Notify evaluation URL with round=2
    post_evaluation_result(data, repo_name)


   


#post end point that takes json input with following fields : email, secret, task, round, nounce, brief, checks, evaluation_url,attachments
@app.post("/handle_task")
async def handle_task(request: Request,background_tasks: BackgroundTasks):
    data = await request.json()
    print("Received data:", data)
    #validate the secret
    if not validate_secret(data.get("secret")):
        return {"status": "error", "message": "Invalid secret"}
       # Add background tasks and return immediately
    round_num = data.get("round")

    if round_num == 1:
        background_tasks.add_task(round1, data)
        message = "Round 1 tasks queued for execution"
    elif round_num == 2:
        background_tasks.add_task(round2, data)
        message = "Round 2 tasks queued for execution"
    else:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid round"}
        )

    # Immediate response (200 OK)
    return JSONResponse(status_code=200, content={"usercode": "..."})
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
