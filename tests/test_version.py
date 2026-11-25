"version test"

from importlib.metadata import version

from packaging.version import parse

from sphinx_doorstop._version import __version__


def test_version() -> None:
    """
    Test the version included in the package. This evaluates whether the version dunder variable from the package is
    equal to the version from the metadata provided by poetry when installing the package. The latter is derived from
    the version in pyproject.toml, and is a strict semantic version (so its string representation might differ
    slightly). Using `parse` from `packaging.version` makes sure that the versions are semantically equal.
    """

    assert parse(__version__) == parse(version(distribution_name="sphinx-doorstop"))
