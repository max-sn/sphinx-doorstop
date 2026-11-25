from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from sphinx_doorstop._version import __version__
from sphinx_doorstop.domain import SphinxDoorstopDomain


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value(
        "doorstop_root",
        default=".",
        rebuild="env",
        types=[Path],
        description="Root directory of the doorstop tree, relative to the Sphinx conf dir.",
    )
    app.add_domain(SphinxDoorstopDomain)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
