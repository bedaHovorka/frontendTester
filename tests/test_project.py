"""Tests for project management."""

import tempfile
from pathlib import Path
from assertpy import assert_that

from frontend_tester.core.project import create_project_structure, find_project_root
from frontend_tester.core.config import ProjectConfig


def test_create_project_structure():
    """Test creating project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        config = ProjectConfig(name="test-project")

        create_project_structure(project_path, config)

        # Check .frontend-tester directories exist (for generated content)
        frontend_tester_dir = project_path / ".frontend-tester"
        assert_that(frontend_tester_dir.exists()).is_true()
        assert_that((frontend_tester_dir / "features").exists()).is_true()
        assert_that((frontend_tester_dir / "steps").exists()).is_true()
        assert_that((frontend_tester_dir / "support").exists()).is_true()
        assert_that((frontend_tester_dir / "baselines").exists()).is_true()
        assert_that((frontend_tester_dir / "reports").exists()).is_true()

        # Check .frontend-tester files exist
        assert_that((frontend_tester_dir / "config.yaml").exists()).is_true()
        assert_that((frontend_tester_dir / "README.md").exists()).is_true()

        # Check TEST_DIR directories exist (for examples)
        test_dir = project_path / "TEST_DIR"
        assert_that(test_dir.exists()).is_true()
        assert_that((test_dir / "features").exists()).is_true()
        assert_that((test_dir / "steps").exists()).is_true()
        assert_that((test_dir / "support").exists()).is_true()

        # Check TEST_DIR files exist
        assert_that((test_dir / "features" / "example.feature").exists()).is_true()
        assert_that((test_dir / "features" / "test_features.py").exists()).is_true()
        assert_that((test_dir / "steps" / "test_common_steps.py").exists()).is_true()
        assert_that((test_dir / "support" / "browser.py").exists()).is_true()
        assert_that((test_dir / "conftest.py").exists()).is_true()
        assert_that((test_dir / "README.md").exists()).is_true()


def test_find_project_root():
    """Test finding project root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        config = ProjectConfig(name="test")

        # Create project
        create_project_structure(project_path, config)

        # Should find from project root
        assert_that(find_project_root(project_path)).is_equal_to(project_path)

        # Should find from subdirectory
        subdir = project_path / "subdir"
        subdir.mkdir()
        assert_that(find_project_root(subdir)).is_equal_to(project_path)

        # Should return None if not in project
        other_dir = Path(tempfile.mkdtemp())
        assert_that(find_project_root(other_dir)).is_none()
