"""Tests for the tech stack detector."""

import pytest

from src.analyzers.detectors.tech_detector import TechDetector
from src.domain.entities import FileNode
from src.domain.enums import Framework, PackageManager, ProjectType


@pytest.fixture
def detector() -> TechDetector:
    return TechDetector()


class TestTechDetector:
    """Tests for technology detection from file tree."""

    def test_detects_python(self, detector: TechDetector):
        tree = [
            FileNode("src/main.py", "main.py", False),
            FileNode("src/models.py", "models.py", False),
            FileNode("pyproject.toml", "pyproject.toml", False),
        ]
        stack = detector.detect(tree, {})
        assert stack.primary_language == ProjectType.PYTHON

    def test_detects_javascript(self, detector: TechDetector):
        tree = [
            FileNode("src/index.js", "index.js", False),
            FileNode("src/app.js", "app.js", False),
            FileNode("package.json", "package.json", False),
        ]
        stack = detector.detect(tree, {})
        assert stack.primary_language == ProjectType.JAVASCRIPT

    def test_detects_fastapi(self, detector: TechDetector):
        tree = [FileNode("main.py", "main.py", False)]
        config = {"dependencies": {"fastapi": ">=0.100"}}
        stack = detector.detect(tree, config)
        assert stack.framework == Framework.FASTAPI

    def test_detects_npm(self, detector: TechDetector):
        tree = [
            FileNode("package.json", "package.json", False),
            FileNode("package-lock.json", "package-lock.json", False),
        ]
        stack = detector.detect(tree, {})
        assert stack.package_manager == PackageManager.NPM

    def test_detects_docker(self, detector: TechDetector):
        tree = [
            FileNode("Dockerfile", "Dockerfile", False),
            FileNode("main.py", "main.py", False),
        ]
        stack = detector.detect(tree, {})
        assert stack.has_docker is True

    def test_detects_tests(self, detector: TechDetector):
        tree = [
            FileNode("tests", "tests", True),
            FileNode("tests/test_main.py", "test_main.py", False),
        ]
        stack = detector.detect(tree, {})
        assert stack.has_tests is True
