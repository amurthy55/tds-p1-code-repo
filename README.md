# GitHub Pages Automation Service

A FastAPI-based microservice that automatically creates GitHub repositories, generates code using AI, and deploys to GitHub Pages based on task briefs. Supports iterative development through a two-round system.

## 🚀 Features

- **Automated Repository Creation**: Creates GitHub repos with MIT license
- **AI-Powered Code Generation**: Uses GPT-4o-mini to generate application code from natural language briefs
- **GitHub Pages Deployment**: Automatically enables and deploys to GitHub Pages
- **Two-Round Development Cycle**:
  - **Round 1**: Generate initial application from task brief
  - **Round 2**: Update existing code based on feedback and checks
- **Asynchronous Processing**: Background task execution for immediate API responses
- **Retry Logic**: Robust error handling with exponential backoff
- **Evaluation Reporting**: Automatically notifies evaluation endpoints with deployment details

## 📋 Prerequisites

- Python 3.11 or above
- GitHub Personal Access Token with repo and pages permissions
- AI Pipe API Key (for LLM access)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn requests openai
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
export AIPIPE_API_KEY="your_aipipe_api_key"
export secret="your_validation_secret"
```

## 🚦 Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://0.0.0.0:8000`

### API Endpoint

**POST** `/handle_task`

#### Request Body Schema

```json
{
  "email": "user@example.com",
  "secret": "your_validation_secret",
  "task": "project-name",
  "round": 1,
  "nonce": "unique_identifier",
  "brief": "Create a simple todo list app with HTML, CSS, and JavaScript",
  "checks": [
    {
      "brief": "Check if app is interactive",
      "checks": [
        {"js": "document.querySelector('button') !== null"}
      ]
    }
  ],
  "evaluation_url": "https://your-evaluation-service.com/notify",
  "attachments": [
    {
      "name": "design.png",
      "url": "https://example.com/design.png"
    }
  ]
}
```

#### Response

```json
{
  "usercode": "..."
}
```

The actual processing happens in the background. Progress is logged to console.

## 🔄 Workflow

### Round 1 Flow
1. Validates request secret
2. Creates GitHub repository: `{task}_{nonce}`
3. Generates code files using AI based on brief
4. Pushes generated files to repository
5. Enables GitHub Pages
6. Notifies evaluation URL with repo details

### Round 2 Flow
1. Fetches all existing files from repository
2. Generates updated code based on:
   - New brief/requirements
   - Previous file contents
   - Evaluation checks
3. Updates files in repository
4. Notifies evaluation URL with updated details

## 📁 Generated Files

The LLM typically generates:
- Application files (e.g., `index.html`, `main.py`, `app.js`)
- `README.md` with:
  - Project summary
  - Setup instructions
  - Usage guide
  - Code explanation
  - License information

## 🔧 Configuration

### GitHub Settings
- **Username**: Configured in `GITHUB_USER` constant (default: `amurthy55`)
- **Repository naming**: `{task}_{nonce}`
- **Branch**: `main`
- **Pages source**: Root directory (`/`)

### AI Settings
- **Model**: `gpt-4o-mini`
- **Temperature**: 0.3 (for consistent output)
- **Response format**: JSON with files array

### Retry Settings
- **File push retries**: 5 attempts with 2-second delays
- **Evaluation post**: Exponential backoff, max 10 minutes

## 🛡️ Security

- Secret validation for all incoming requests
- GitHub token stored as environment variable
- Bearer token authentication for API calls

## 📊 Monitoring

The service logs:
- Repository creation status
- File push operations
- GitHub Pages enablement
- Evaluation endpoint responses
- Error messages with details

Example log output:
```
Executing Round 1 tasks...
Repository project-name_abc123 created successfully.
✅ Pushed index.html
✅ Pushed README.md
GitHub Pages enabled for repository project-name_abc123.
✅ Evaluation URL accepted payload.
```

## 🐛 Troubleshooting

### Common Issues

**404 errors when fetching repo contents**
- Ensure repository name matches exactly (check for underscores)
- Wait for GitHub propagation (retry logic handles this)

**Multiple GitHub Pages build cancellations**
- Files are pushed individually; consider batching updates
- Each push triggers a new build, canceling previous ones

**LLM response parsing errors**
- Check AI Pipe API key validity
- Verify model availability
- Review prompt format

**Evaluation endpoint not responding**
- Service retries with exponential backoff
- Check endpoint availability
- Verify payload format matches expected schema

## 📝 License

MIT License - See generated repositories for full license text

## 🤝 Contributing

This is an automation service. To extend functionality:
1. Modify `write_code_with_llm()` for different AI models
2. Update `push_files_to_repo()` for batch operations
3. Add new endpoints for additional automation tasks

## 📧 Support

For issues related to:
- **GitHub API**: Check token permissions and rate limits
- **AI Generation**: Verify AI Pipe API key and model availability
- **Deployment**: Review GitHub Pages settings in repository

## 🔗 Related Links

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AI Pipe Documentation](https://aipipe.org/)
