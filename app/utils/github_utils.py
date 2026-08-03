import base64
import re


def encode_content_to_base64(content: str) -> str:
    """
    GitHub's Contents API requires file content to be base64-encoded.
    """
    return base64.b64encode(content.encode("utf-8")).decode("utf-8")


def slugify_repo_name(raw_name: str) -> str:
    """
    Normalize a user-provided or AI-suggested name into a GitHub-safe repo slug.
    Example: "My Cool Project!!" -> "my-cool-project"
    """
    name = raw_name.strip().lower()
    name = re.sub(r"[^a-z0-9\-_]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name or "untitled-project"


def parse_github_error_message(response_json: dict) -> str:
    """
    GitHub error payloads look like:
    {"message": "Repository creation failed.", "errors": [{"message": "name already exists on this account"}]}
    This extracts the most useful human-readable message.
    """
    base_message = response_json.get("message", "Unknown GitHub API error.")
    errors = response_json.get("errors") or []

    if errors:
        detail_messages = [
            err.get("message", "") for err in errors if isinstance(err, dict) and err.get("message")
        ]
        if detail_messages:
            return f"{base_message}: {'; '.join(detail_messages)}"

    return base_message


def default_readme_content(repo_name: str, description: str = "") -> str:
    """
    Hardcoded README template used for initial testing (no AI generation yet).
    """
    description_line = description.strip() or "Project description goes here."

    return (
        f"# {repo_name}\n\n"
        f"{description_line}\n\n"
        "## Getting Started\n\n"
        "This repository was created automatically via the AI Software Engineering Agent.\n\n"
        "## Status\n\n"
        "- [x] Repository initialized\n"
        "- [ ] Project scaffolding\n"
        "- [ ] CI/CD setup\n"
    )


def default_gitignore_content() -> str:
    """
    Minimal hardcoded .gitignore used for initial testing.
    """
    return (
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "node_modules/\n"
        ".venv/\n"
        "dist/\n"
        "build/\n"
    )
