"""Installation section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.domain.enums import PackageManager, ProjectType
from src.generators.templates import INSTALLATION_TEMPLATE

__all__ = ["InstallationGenerator"]

_INSTALL_COMMANDS: dict[PackageManager, str] = {
    PackageManager.PIP: "pip install -r requirements.txt",
    PackageManager.POETRY: "poetry install",
    PackageManager.NPM: "npm install",
    PackageManager.YARN: "yarn",
    PackageManager.PNPM: "pnpm install",
    PackageManager.BUN: "bun install",
    PackageManager.CARGO: "cargo build",
    PackageManager.GO_MOD: "go mod download",
    PackageManager.MAVEN: "mvn install",
    PackageManager.GRADLE: "gradle build",
    PackageManager.COMPOSER: "composer install",
    PackageManager.BUNDLER: "bundle install",
}

_RUN_COMMANDS: dict[PackageManager, str] = {
    PackageManager.PIP: "python -m src",
    PackageManager.POETRY: "poetry run python -m src",
    PackageManager.NPM: "npm start",
    PackageManager.YARN: "yarn start",
    PackageManager.PNPM: "pnpm start",
    PackageManager.BUN: "bun start",
    PackageManager.CARGO: "cargo run",
    PackageManager.GO_MOD: "go run .",
    PackageManager.MAVEN: "mvn spring-boot:run",
    PackageManager.GRADLE: "gradle bootRun",
    PackageManager.COMPOSER: "php artisan serve",
    PackageManager.BUNDLER: "rails server",
}

_PREREQUISITES: dict[ProjectType, str] = {
    ProjectType.PYTHON: "- Python 3.10+",
    ProjectType.JAVASCRIPT: "- Node.js 18+\n- npm / yarn / pnpm",
    ProjectType.TYPESCRIPT: "- Node.js 18+\n- npm / yarn / pnpm",
    ProjectType.GO: "- Go 1.21+",
    ProjectType.RUST: "- Rust (latest stable)\n- Cargo",
    ProjectType.JAVA: "- Java 17+\n- Maven or Gradle",
    ProjectType.RUBY: "- Ruby 3.1+\n- Bundler",
    ProjectType.CSHARP: "- .NET 8+",
    ProjectType.PHP: "- PHP 8.2+\n- Composer",
}


class InstallationGenerator:
    """Generates the Getting Started / Installation section."""

    ORDER = 20

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the installation section with clone, install, and run commands.

        Detects the package manager and generates appropriate commands.
        Includes prerequisites based on the primary language.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered installation markdown.
        """
        pm = repo_info.tech_stack.package_manager
        lang = repo_info.tech_stack.primary_language

        install_cmd = _INSTALL_COMMANDS.get(pm, "# See project documentation")
        run_cmd = _RUN_COMMANDS.get(pm, "# See project documentation")
        prerequisites = _PREREQUISITES.get(lang, "- See project documentation")

        # Enhance prerequisites with version info if available
        if repo_info.tech_stack.python_version:
            prerequisites = f"- Python {repo_info.tech_stack.python_version}+"
        if repo_info.tech_stack.node_version:
            prerequisites = f"- Node.js {repo_info.tech_stack.node_version}+"

        # Check for pyproject.toml with pip — prefer editable install
        if pm == PackageManager.PIP:
            has_pyproject = any(node.name == "pyproject.toml" for node in repo_info.tree if not node.is_dir)
            if has_pyproject:
                install_cmd = "pip install -e ."

        content = INSTALLATION_TEMPLATE.format(
            prerequisites=prerequisites,
            owner=repo_info.owner,
            repo=repo_info.name,
            package_manager_instructions=install_cmd,
            run_command=run_cmd,
        )

        return Section(
            title="Getting Started",
            content=content,
            order=self.ORDER,
            enabled=True,
        )
