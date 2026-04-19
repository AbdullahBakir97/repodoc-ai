"""Markdown template strings for README generation."""

__all__ = [
    "HEADER_TEMPLATE",
    "INSTALLATION_TEMPLATE",
    "STRUCTURE_TEMPLATE",
    "API_TEMPLATE",
    "CHANGELOG_TEMPLATE",
    "CONTRIBUTING_TEMPLATE",
    "FOOTER_TEMPLATE",
]

HEADER_TEMPLATE = """# {title}

{badges}

{description}"""

INSTALLATION_TEMPLATE = """## Getting Started

### Prerequisites

{prerequisites}

### Installation

```bash
# Clone the repository
git clone https://github.com/{owner}/{repo}.git
cd {repo}

# Install dependencies
{package_manager_instructions}
```

### Running

```bash
{run_command}
```"""

STRUCTURE_TEMPLATE = """## Project Structure

```
{tree}
```"""

API_TEMPLATE = """## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
{endpoints}"""

CHANGELOG_TEMPLATE = """## Recent Changes

{entries}"""

CONTRIBUTING_TEMPLATE = """## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please make sure to:
- Update tests as appropriate
- Follow the existing code style
- Write clear commit messages"""

FOOTER_TEMPLATE = """## License

This project is licensed under the {license} License. See the [LICENSE](LICENSE) file for details.

---

{links}"""
