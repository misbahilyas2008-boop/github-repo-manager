# github-repo-manager  
**⚙️ Automate GitHub repository workflows with a lightweight Python API**

[Table of Contents](#table-of-contents)

## 📖 Overview  
`github-repo-manager` is a minimal FastAPI application that streamlines common GitHub repository operations—such as creation, visibility toggling, and status updates—by leveraging OAuth authentication and the GitHub REST API. Built with Python, it abstracts the intricacies of GitHub’s API, providing a clean, reusable service layer for developers and teams.

## 🎯 Purpose  
- Simplify routine GitHub repository tasks for developers and DevOps teams.  
- Centralize OAuth and API configuration to avoid hard‑coding URLs and secrets.  
- Offer a RESTful interface that can be integrated into CI/CD pipelines or internal tooling.  
- Provide a clear separation of concerns: configuration, services, controllers, and data models.  
- Enable rapid prototyping of GitHub automation scripts without a full framework overhead.

## 🚀 Features  
### Repository Management  
- Create new repositories with configurable visibility (public/private).  
- Update repository status and metadata.  
- Check for existing repositories to avoid duplicates.  

### GitHub Integration  
- Centralized OAuth handling (`GitHubConfig`).  
- HTTP client (`httpx`) for authenticated requests.  
- Error parsing and custom exception handling (`GitHubAPIException`, `RepositoryAlreadyExistsException`).  

### Utilities  
- Base64 encoding for GitHub’s Contents API.  
- URL query string construction via `urllib.parse.urlencode`.  

### Data Persistence  
- SQLAlchemy ORM models with PostgreSQL UUID support.  
- Session management abstraction (`app/database/session.py`).  

### API Layer  
- FastAPI routes (`app/routes/repository_routes.py`) exposing CRUD endpoints.  
- Dependency injection for current user and repository services.  

## 🛠️ Tech Stack  
| Component | Description |
|-----------|-------------|
| **Python 3.10+** | Core language |
| **FastAPI** | Web framework for routing and dependency injection |
| **SQLAlchemy** | ORM for database interactions |
| **PostgreSQL** | Relational database (UUID support) |
| **httpx** | Async HTTP client for GitHub API calls |
| **Pydantic** | Data validation and serialization |
| **dotenv / config.settings** | Environment configuration (implied) |

## 📦 Project Structure  
- **`app/config/github.py`** – Holds all GitHub OAuth and API URLs, secrets, and helper functions.  
- **`app/controllers/repository_controller.py`** – Business logic for repository operations; translates service results into HTTP responses.  
- **`app/core/exceptions.py`** – Custom exception hierarchy for clean error handling.  
- **`app/database/session.py`** – SQLAlchemy session factory; ensures a single session per request.  
- **`app/dependencies/repository_dependencies.py`** – FastAPI dependencies that inject the current user and repository service into routes.  
- **`app/models/repository.py`** – SQLAlchemy ORM model representing a GitHub repository record.  
- **`app/routes/repository_routes.py`** – FastAPI router exposing endpoints for repository CRUD actions.  
- **`app/schemas/repository.py`** – Pydantic schemas for request/response validation.  
- **`app/services/github_service.py`** – Wrapper around GitHub’s REST API, handling authentication, request building, and error parsing.  
- **`app/utils/github_utils.py`** – Small helpers for content encoding and URL manipulation.

## 🏁 Getting Started  

### Prerequisites  
- Python 3.10+  
- PostgreSQL (or a compatible database)  
- GitHub account with an OAuth app set up (client ID & secret)

### Installation  
```bash
# Clone the repo
git clone https://github.com/your-username/github-repo-manager.git
cd github-repo-manager

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

> **Tip:** If `requirements.txt` is missing, generate one with `pip freeze > requirements.txt` after installing the packages listed in `pyproject.toml` or `setup.py`.

### Configuration  
Create a `.env` file at the project root with the following (replace placeholders):

```
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Running the Application  
```bash
uvicorn app.main:app --reload
```

> The `app.main` module should expose the FastAPI `app` instance. If it’s named differently, adjust the command accordingly.

### Testing the API  
```bash
# Example: Create a repository
curl -X POST http://localhost:8000/repositories \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-repo","visibility":"public"}'
```

## 🤝 Contributing  
We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues, feature requests, and pull requests.

## 📊 Status  
- [x] Repository initialized  
- [x] Project scaffolding  
- [ ] CI/CD setup  

---