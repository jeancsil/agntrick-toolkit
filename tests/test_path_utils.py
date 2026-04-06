"""Tests for path validation utilities."""


import pytest

from agntrick_toolbox.path_utils import (
    PathValidationError,
    validate_output_path,
    validate_workspace_path,
)


class TestValidateWorkspacePath:
    """Tests for validate_workspace_path function."""

    def test_accepts_path_inside_workspace(self, temp_workspace, monkeypatch):
        """Must accept paths inside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        result = validate_workspace_path("test.txt")
        assert str(temp_workspace) in str(result)

    def test_accepts_absolute_path_inside_workspace(self, temp_workspace, monkeypatch):
        """Must accept absolute paths inside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        # Create a file inside workspace
        test_file = temp_workspace / "test.txt"
        test_file.touch()

        result = validate_workspace_path(str(test_file))
        # Use resolve() to handle macOS /var -> /private/var symlink
        assert result.resolve() == test_file.resolve()

    def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Must reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        with pytest.raises(PathValidationError) as exc_info:
            validate_workspace_path("/etc/passwd")

        assert "outside workspace" in str(exc_info.value)

    def test_rejects_path_traversal(self, temp_workspace, monkeypatch):
        """Must reject ../ traversal attempts."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        with pytest.raises(PathValidationError):
            validate_workspace_path("../../../etc/passwd")

    def test_rejects_absolute_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Must reject absolute paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        with pytest.raises(PathValidationError):
            validate_workspace_path("/root/.ssh/id_rsa")


class TestValidateOutputPath:
    """Tests for validate_output_path function."""

    def test_creates_parent_directories(self, temp_workspace, monkeypatch):
        """Should create parent directories if they don't exist."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        result = validate_output_path("subdir/nested/output.txt")

        assert result.parent.exists()
        assert str(temp_workspace) in str(result)

    def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Must reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(
            path_utils.settings,
            "toolbox_workspace",
            str(temp_workspace),
        )

        with pytest.raises(PathValidationError):
            validate_output_path("/tmp/output.txt")
