import tomllib  # Python 3.11+
from pathlib import Path

def test_version_matches_pyproject():
    import pypipe
    with open(Path(__file__).parents[1] / "pyproject.toml", "rb") as f:
        version = tomllib.load(f)["project"]["version"]
    assert pypipe.__version__ == version
