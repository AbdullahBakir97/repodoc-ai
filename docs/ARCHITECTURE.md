# RepoDoc AI - System Design Document

## 1. Overview

**RepoDoc AI** is a GitHub App that automatically generates and maintains high-quality README.md files by analyzing your repository's structure, code, commits, and configuration files.

## 2. Core Features

| Feature | Description |
|---------|-------------|
| **Structure Scanner** | Maps directory tree, detects project type, framework |
| **Tech Detector** | Identifies languages, frameworks, package managers, CI tools |
| **Commit Analyzer** | Extracts recent changes, generates changelog entries |
| **README Generator** | Produces complete README with all sections |
| **Badge Generator** | Creates status badges (CI, version, license, coverage) |
| **PR Creator** | Opens a PR with the generated/updated README |
| **Config File Parser** | Reads package.json, pyproject.toml, Cargo.toml, etc |
| **API Docs Extractor** | Finds routes, endpoints, CLI commands from code |

## 3. Architecture (Clean Architecture)

```
API Layer         → FastAPI routes, webhook handler, dashboard
Application Layer → Orchestrator, PR workflow, generation pipeline
Domain Layer      → Entities, generators, templates (pure logic)
Infrastructure    → GitHub client, file reader, config parser
```

## 4. Data Flow

```
Trigger (push to main / manual / scheduled)
    │
    ▼
[Repo Scanner] ── scans tree, reads key files
    │
    ▼
[Tech Detector] ── identifies stack, frameworks, tools
    │
    ▼
[Commit Analyzer] ── recent commits, contributors
    │
    ▼
[README Generator] ── assembles sections from templates
    │
    ▼
[PR Creator] ── opens PR with generated README
```

## 5. README Sections Generated

1. **Title & Description** — from package.json/pyproject.toml/repo description
2. **Badges** — CI status, version, license, language, downloads
3. **Features** — from code structure and docs
4. **Tech Stack** — detected languages, frameworks, tools
5. **Project Structure** — directory tree with descriptions
6. **Getting Started** — prerequisites, installation, running
7. **API Reference** — endpoints/commands if detected
8. **Configuration** — env vars, config files
9. **Testing** — how to run tests
10. **Deployment** — Docker, CI/CD if detected
11. **Contributing** — standard contributing guide
12. **License** — from LICENSE file
13. **Changelog** — from recent commits

## 6. Project Structure

```
repodoc-ai/
├── src/
│   ├── domain/
│   │   ├── entities.py          # RepoInfo, TechStack, Section, ReadmeDoc
│   │   ├── enums.py             # ProjectType, Language, Framework, PackageManager
│   │   ├── interfaces.py        # IScanner, IDetector, IGenerator
│   │   └── exceptions.py        # Custom exceptions
│   ├── analyzers/
│   │   ├── scanners/
│   │   │   ├── repo_scanner.py  # Scans directory tree via GitHub API
│   │   │   ├── file_parser.py   # Parses package.json, pyproject.toml, etc
│   │   │   └── commit_analyzer.py # Analyzes commit history
│   │   └── detectors/
│   │       ├── tech_detector.py # Detects languages, frameworks
│   │       ├── ci_detector.py   # Detects CI/CD setup
│   │       └── api_detector.py  # Detects API routes/endpoints
│   ├── generators/
│   │   ├── readme_generator.py  # Main README assembler
│   │   ├── section_generators/
│   │   │   ├── header.py        # Title, description, badges
│   │   │   ├── installation.py  # Getting started section
│   │   │   ├── structure.py     # Project structure tree
│   │   │   ├── api_docs.py      # API reference section
│   │   │   ├── changelog.py     # Changelog from commits
│   │   │   └── footer.py        # License, contributing, links
│   │   ├── badge_generator.py   # Shield.io badge URLs
│   │   └── templates.py         # Markdown templates
│   ├── application/
│   │   ├── orchestrator.py      # Coordinates scan → detect → generate
│   │   ├── pr_workflow.py       # Creates branch, commits, opens PR
│   │   └── webhook_handler.py   # Routes GitHub events
│   ├── infrastructure/
│   │   ├── github/
│   │   │   ├── client.py        # GitHub API client (reused pattern)
│   │   │   ├── auth.py          # JWT auth (reused)
│   │   │   └── webhook.py       # Signature verification (reused)
│   │   └── config/
│   │       ├── schema.py        # Per-repo .github/repodoc.yml config
│   │       └── loader.py        # Config loader
│   ├── api/
│   │   ├── app.py               # FastAPI app factory
│   │   ├── routes/
│   │   │   ├── webhook.py       # POST /webhook
│   │   │   ├── generate.py      # POST /api/v1/generate (manual trigger)
│   │   │   └── health.py        # GET /health
│   │   └── middleware/
│   │       ├── error_handler.py
│   │       └── logging.py
│   ├── config/
│   │   ├── settings.py          # Environment settings
│   │   └── logging.py           # Logging config
│   ├── container.py             # DI container
│   └── main.py                  # Entry point
├── dashboard/
│   └── index.html               # Landing page
├── tests/
├── pyproject.toml
├── Dockerfile
├── render.yaml
└── README.md
```

## 7. Tech Stack

Python 3.12+ | FastAPI | Pydantic v2 | httpx | PyJWT | Docker | Render
