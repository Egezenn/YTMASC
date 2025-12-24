import pytest
from pathlib import Path
import sys

# Add project root to path so we can import ytmasc
# This assumes tests/ is at the root level alongside ytmasc/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_working_dir(tmp_path):
    """Provides a temporary directory for tests to use as a working dir."""
    return tmp_path
