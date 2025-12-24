import pytest
from unittest.mock import patch
from click.testing import CliRunner
from ytmasc import utils
from ytmasc.__main__ import cli


def test_parse_extras():
    """Test the parse_extras utility function."""
    assert utils.parse_extras("cover,lyric") == ["cover", "lyric"]
    assert utils.parse_extras(" cover , lyric ") == ["cover", "lyric"]
    assert utils.parse_extras("") == []
    assert utils.parse_extras(None) == []


def test_cli_help():
    """Smoke test to ensure the CLI help command runs without error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "YTMASC" in result.output
    # The output might vary, check basic presence
    assert "Download a single video" in result.output


def test_check_dependencies(capsys):
    """Test that check_dependencies prints errors and exits if binaries are missing."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(SystemExit) as excinfo:
            utils.check_dependencies()

        assert excinfo.value.code == 1

        # Check output
        captured = capsys.readouterr()
        assert "ERROR: Required dependencies not found" in captured.out
        # Verify that yt-dlp is one of the checked dependencies
        assert "yt-dlp" in captured.out
