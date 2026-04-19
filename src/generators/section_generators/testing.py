"""Testing section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.domain.enums import PackageManager, ProjectType

__all__ = ["TestingGenerator"]

_TEST_COMMANDS: dict[ProjectType, dict[str, str]] = {
    ProjectType.PYTHON: {
        "runner": "pytest",
        "command": "pytest",
        "alt_command": "python -m pytest",
    },
    ProjectType.JAVASCRIPT: {
        "runner": "Jest / Vitest",
        "command": "npm test",
    },
    ProjectType.TYPESCRIPT: {
        "runner": "Jest / Vitest",
        "command": "npm test",
    },
    ProjectType.GO: {
        "runner": "go test",
        "command": "go test ./...",
    },
    ProjectType.RUST: {
        "runner": "cargo test",
        "command": "cargo test",
    },
    ProjectType.JAVA: {
        "runner": "JUnit",
        "command": "mvn test",
    },
    ProjectType.RUBY: {
        "runner": "RSpec",
        "command": "bundle exec rspec",
    },
    ProjectType.PHP: {
        "runner": "PHPUnit",
        "command": "vendor/bin/phpunit",
    },
}

_PM_TEST_COMMANDS: dict[PackageManager, str] = {
    PackageManager.NPM: "npm test",
    PackageManager.YARN: "yarn test",
    PackageManager.PNPM: "pnpm test",
    PackageManager.BUN: "bun test",
    PackageManager.POETRY: "poetry run pytest",
}


class TestingGenerator:
    """Generates the Testing section with test runner detection."""

    ORDER = 45

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the testing section.

        Detects the test runner from the project type and package manager,
        then generates appropriate run commands.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered testing markdown,
            or a disabled section if no tests are detected.
        """
        if not repo_info.tech_stack.has_tests:
            return Section(
                title="Testing",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        lang = repo_info.tech_stack.primary_language
        pm = repo_info.tech_stack.package_manager

        test_info = _TEST_COMMANDS.get(lang)
        if test_info is None:
            test_runner = "N/A"
            test_command = "# See project documentation for test instructions"
        else:
            test_runner = test_info["runner"]
            # Prefer package-manager-specific command if available
            test_command = _PM_TEST_COMMANDS.get(pm, test_info["command"])

        lines = [
            "## Testing",
            "",
            f"This project uses **{test_runner}** for testing.",
            "",
            "```bash",
            f"{test_command}",
            "```",
        ]

        return Section(
            title="Testing",
            content="\n".join(lines),
            order=self.ORDER,
            enabled=True,
        )
