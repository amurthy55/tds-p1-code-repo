# 🚀 FastAPI GitHub Automation API

This Space hosts a FastAPI-based backend that automates:
- Creating GitHub repositories
- Uploading files
- Enabling GitHub Pages
- Integrating with LLM-generated content

---

## 🧠 Features
- Secure request validation using a shared secret
- Uses GitHub REST API with token authentication
- Supports two execution rounds (Round 1 & Round 2)
- Auto-publishes a simple HTML demo to GitHub Pages

---

## 🧩 API Endpoint
### `POST /handle_task`

#### Example Input:
```json
{
  "email": "user@example.com",
  "secret": "YOUR_SECRET_HERE",
  "task": "demo",
  "round": 1,
  "nonce": "12345",
  "brief": "create simple html",
  "checks": [],
  "evaluation_url": "",
  "attachments": []
}
