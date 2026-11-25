from typing import TYPE_CHECKING, ClassVar

from docutils.parsers.rst import Directive
from sphinx.domains import Domain
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

from sphinx_doorstop.directives import SphinxDoorstopDocumentDirective
from sphinx_doorstop.models import SphinxDoorstopDocument, SphinxDoorstopItem

if TYPE_CHECKING:
    from sphinx.util.typing import RoleFunction


class SphinxDoorstopDomain(Domain):
    name = "doorstop"
    label = "Doorstop"
    roles: ClassVar[dict[str, "RoleFunction"]] = {
        "ref": XRefRole(),
    }
    directives: ClassVar[dict[str, type[Directive]]] = {
        "document": SphinxDoorstopDocumentDirective
    }
    # indices: ClassVar[list[type[Index]]] = [ItemIndex]
    initial_data: ClassVar[
        dict[str, list[SphinxDoorstopItem] | list[SphinxDoorstopDocument]]
    ] = {
        "items": [],  # object list
        "documents": [],  # object list
    }

    data_version = 0

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        target = target.removesuffix(".md").removesuffix(".MD")
        matches = [doc for doc in self.get_documents() if doc.prefix == target] + [
            item for item in self.get_items() if item.uid == target
        ]

        return [
            (
                "doorstop:ref",
                make_refnode(
                    builder,
                    fromdocname,
                    match.sphinx_doc_name,
                    match.anchor,
                    contnode,
                    target,
                ),
            )
            for match in matches
        ]

    def add_document(self, document: SphinxDoorstopDocument) -> None:
        self.data["documents"].append(document)

    def add_item(self, item: SphinxDoorstopItem) -> None:
        self.data["items"].append(item)

    def get_items(self) -> list[SphinxDoorstopItem]:
        return self.data["items"]

    def get_documents(self) -> list[SphinxDoorstopDocument]:
        return self.data["documents"]

    def clear_doc(self, docname: str) -> None:
        self.data["items"] = [
            item for item in self.data["items"] if item.sphinx_doc_name != docname
        ]
        self.data["documents"] = [
            doc for doc in self.data["documents"] if doc.sphinx_doc_name != docname
        ]
