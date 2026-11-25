from dataclasses import dataclass

import doorstop


@dataclass
class SphinxDoorstopItem:
    uid: str
    sphinx_doc_name: str
    source: doorstop.Item
    priority: int = 0

    @property
    def anchor(self) -> str:
        return f"doorstop-item-{self.uid}"


@dataclass
class SphinxDoorstopDocument:
    prefix: str
    sphinx_doc_name: str
    source: doorstop.Document
    sep: str | None = None
    priority: int = 0

    @property
    def anchor(self) -> str:
        return f"doorstop-doc-{self.prefix}"
