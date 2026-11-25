from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import doorstop


def get_document_title(doc: "doorstop.Document") -> str:
    """Return title from the doorstop document."""
    if doc._attribute_defaults:
        return doc._attribute_defaults.get("doc", {}).get("title", doc.prefix)
    return doc.prefix
