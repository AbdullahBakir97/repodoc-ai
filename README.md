# RepoDoc AI

A GitHub App that automatically generates and maintains high-quality README.md files by analyzing your repository's structure, code, commits, and configuration.

## The Problem

Every developer knows they should write good documentation, but most READMEs are incomplete, outdated, or missing entirely. Writing and maintaining docs is tedious, especially as projects evolve.

## What RepoDoc AI Does

Install it on your repo, push to main, and get a **pull request** with a professionally generated README containing:

- **Project description** from your package config
- **Badges** (CI status, language, license, framework)
- **Features list** from your code structure
- **Tech stack table** (auto-detected language, framework, tools)
- **Project structure** (ASCII tree with descriptions)
- **Installation instructions** (detects your package manager)
- **API reference** (finds routes/endpoints in your code)
- **Testing guide** (detects test framework and commands)
- **Recent changelog** (from commit history)
- **Contributing guide** and license info

## How It Works

1. **Install** RepoDoc AI on your repositories
2. **Push** to your default branch
3. RepoDoc AI **scans** your repo structure, config files, and commits
4. A **pull request** appears with a generated/updated README.md
5. **Review and merge** — done!

## Tech Stack

Python 3.12+ | FastAPI | Pydantic v2 | httpx | PyJWT | Docker

## Configuration

Add `.github/repodoc.yml` to customize:

```yaml
enabled: true
trigger: push          # push | manual
branch: repodoc/update-readme

sections:
  header: true
  features: true
  tech_stack: true
  installation: true
  structure: true
  api_docs: true
  changelog: true
  testing: true
  contributing: true
  license: true

exclude_dirs:
  - node_modules
  - .git
  - __pycache__
  - .venv

max_depth: 3
```

## Architecture

Built with Clean Architecture and SOLID principles:

```
API Layer         → FastAPI webhooks, generation endpoint, dashboard
Application Layer → Generation orchestrator, PR workflow
Domain Layer      → Entities, generators, templates (pure logic)
Infrastructure    → GitHub API client, config loader
```

## Deployment

```bash
# Docker
docker build -t repodoc-ai .
docker run -p 8000:8000 --env-file .env repodoc-ai
```

## License

MIT
