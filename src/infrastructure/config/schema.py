"""Per-repository configuration schema for RepoDoc AI.

Repositories can customise README generation by placing a
``.github/repodoc.yml`` file in their default branch.
"""

from pydantic import BaseModel, Field

__all__ = ["RepodocConfig", "SectionsConfig"]


class SectionsConfig(BaseModel):
    """Controls which sections appear in the generated README."""

    header: bool = True
    features: bool = True
    tech_stack: bool = True
    installation: bool = True
    structure: bool = True
    api_docs: bool = True
    changelog: bool = True
    testing: bool = True
    contributing: bool = True
    license: bool = True


class RepodocConfig(BaseModel):
    """Per-repository configuration loaded from ``.github/repodoc.yml``.

    All fields have sensible defaults so the config file is entirely
    optional.
    """

    enabled: bool = True
    trigger: str = "push"  # push | manual | schedule
    branch: str = "repodoc/update-readme"
    sections: SectionsConfig = Field(default_factory=SectionsConfig)
    exclude_dirs: list[str] = Field(
        default_factory=lambda: [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "dist",
            "build",
        ]
    )
    max_depth: int = 3
