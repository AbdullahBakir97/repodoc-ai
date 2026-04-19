"""Main README generator that orchestrates all section generators."""

from __future__ import annotations

from src.domain.entities import ReadmeDocument, RepoInfo, Section
from src.generators.badge_generator import BadgeGenerator
from src.generators.section_generators.api_docs import APIDocsGenerator
from src.generators.section_generators.changelog import ChangelogGenerator
from src.generators.section_generators.features import FeaturesGenerator
from src.generators.section_generators.footer import FooterGenerator
from src.generators.section_generators.header import HeaderGenerator
from src.generators.section_generators.installation import InstallationGenerator
from src.generators.section_generators.structure import StructureGenerator
from src.generators.section_generators.tech_stack import TechStackGenerator
from src.generators.section_generators.testing import TestingGenerator

__all__ = ["ReadmeGenerator"]


class ReadmeGenerator:
    """Assembles a complete README from individual section generators.

    Each section generator produces a Section with an order value.
    Sections are collected, filtered by their enabled flag, and
    assembled into a ReadmeDocument sorted by order.
    """

    def __init__(self) -> None:
        self._section_generators: list[
            HeaderGenerator
            | FeaturesGenerator
            | TechStackGenerator
            | InstallationGenerator
            | StructureGenerator
            | APIDocsGenerator
            | TestingGenerator
            | ChangelogGenerator
            | FooterGenerator
        ] = [
            HeaderGenerator(),
            FeaturesGenerator(),
            TechStackGenerator(),
            InstallationGenerator(),
            StructureGenerator(),
            APIDocsGenerator(),
            TestingGenerator(),
            ChangelogGenerator(),
            FooterGenerator(),
        ]
        self._badge_generator = BadgeGenerator()

    def generate(self, repo_info: RepoInfo) -> ReadmeDocument:
        """Generate a complete README document from repository information.

        Runs each section generator and collects enabled sections
        into a ReadmeDocument.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A ReadmeDocument containing all enabled sections.
        """
        sections: list[Section] = []

        for gen in self._section_generators:
            section = gen.generate(repo_info)
            if section.enabled:
                sections.append(section)

        return ReadmeDocument(sections=sections)
