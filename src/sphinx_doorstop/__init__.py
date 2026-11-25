from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, cast

import doorstop
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from doorstop import build
from myst_parser.parsers.docutils_ import Parser
from myst_parser.parsers.sphinx_ import MystParser
from sphinx.application import Sphinx
from sphinx.domains import Domain
from sphinx.errors import SphinxError
from sphinx.roles import XRefRole
from sphinx.util.docutils import SphinxDirective, new_document
from sphinx.util.nodes import make_refnode
from sphinx.util.typing import ExtensionMetadata, RoleFunction

from sphinx_doorstop._version import __version__


class DoorstopError(SphinxError):
    category = "doorstop"


@dataclass
class DoorstopItem:
    uid: str
    sphinx_doc_name: str
    source: doorstop.Item
    priority: int = 0

    @property
    def anchor(self) -> str:
        return f"doorstop-item-{self.uid}"


@dataclass
class DoorstopDocument:
    prefix: str
    sphinx_doc_name: str
    source: doorstop.Document
    sep: str | None = None
    priority: int = 0

    @property
    def anchor(self) -> str:
        return f"doorstop-doc-{self.prefix}"


class DoorstopDocumentDirective(SphinxDirective):
    required_arguments = 1
    has_content = False

    option_spec = {  # noqa: RUF012
        "numbered": directives.flag,
    }

    def run(self) -> list[nodes.Node]:

        doorstop_root = (Path(self.env.srcdir) / self.config["doorstop_root"]).resolve()
        doc_name = self.arguments[0]

        # Try to build the doorstop tree, but raise an error on failure
        try:
            tree = build(root=doorstop_root)
        except doorstop.common.DoorstopError as e:
            raise DoorstopError(
                f"Failed to build doorstop tree in {doorstop_root}"
            ) from e

        # Try to find the specified document in the tree, but raise an error when it is not found
        try:
            doc = tree.find_document(doc_name)
        except doorstop.common.DoorstopError as e:
            raise DoorstopError(
                f"Doorstop document {doc_name} not found in {doorstop_root}"
            ) from e

        # Add the document config file to the document dependencies
        self.env.note_dependency(doc.config)

        doorstop_document = DoorstopDocument(
            prefix=doc.prefix,
            sphinx_doc_name=self.env.current_document.docname,
            source=doc,
            sep=doc.sep,
        )

        domain = cast(DoorstopDomain, self.env.get_domain("doorstop"))
        domain.add_document(doorstop_document)

        if hasattr(self.env, "myst_config"):
            markdown_parser = MystParser()
        else:
            markdown_parser = Parser()

        document_level_section = nodes.section(
            ids=[doorstop_document.anchor], names=[doc.prefix]
        )
        document_title = get_document_title(doc)
        target_node = nodes.target("", "", ids=[doorstop_document.anchor])
        title_node = nodes.title(document_title, document_title)

        document_level_section += title_node
        document_level_section += target_node

        # Create a list of sections for all items, not yet nested based on depth
        item_sections = [
            (
                item.depth - 1,
                self.create_item_section(item, domain, markdown_parser),
            )
            for item in doc.items
        ]

        # Also add all items to the document dependencies
        for item in doc.items:
            self.env.note_dependency(item.path)

        for depth, item_section in item_sections:
            last_section_of_current_level = document_level_section
            for _ in range(depth):
                last_section_of_current_level = last_section_of_current_level.children[
                    -1
                ]
            last_section_of_current_level += item_section

        return [document_level_section]

    def create_item_section(
        self,
        item: doorstop.Item,
        domain: "DoorstopDomain",
        markdown_parser: MystParser | Parser,
    ) -> nodes.section:
        doorstop_item = DoorstopItem(
            uid=str(item.uid),
            sphinx_doc_name=self.env.current_document.docname,
            source=item,
        )
        domain.add_item(doorstop_item)
        section = nodes.section(ids=[doorstop_item.anchor], names=[item.header])

        # Add heading and hyperlink target
        heading = item.header
        if "numbered" in self.options:
            heading = f"{item.level} {heading}"
        section += nodes.title(heading, heading)
        section += nodes.target("", "", ids=[doorstop_item.anchor])

        fields = nodes.field_list()

        for name, value in [
            ("UID", doorstop_item.uid),
            ("Status", item.attribute("status")),
        ]:
            if value is not None:
                field = nodes.field()

                field += nodes.field_name(text=name)
                body = nodes.field_body()

                body += nodes.paragraph(text=str(value))

                field += body
                fields += field

        section += fields

        docutils_doc = new_document(
            "<doorstop-item>",
            settings=self.state.document.settings,
        )

        markdown_parser.parse(doorstop_item.source.text, docutils_doc)

        # Add all parsed nodes from the markdown contents directly to the section
        for child in docutils_doc.children:
            section += child

        return section


class DoorstopDomain(Domain):
    name = "doorstop"
    label = "Doorstop"
    roles: ClassVar[dict[str, RoleFunction]] = {
        "ref": XRefRole(),
    }
    directives: ClassVar[dict[str, type[Directive]]] = {
        "document": DoorstopDocumentDirective
    }
    # indices: ClassVar[list[type[Index]]] = [ItemIndex]
    initial_data: ClassVar[dict[str, list[DoorstopItem] | list[DoorstopDocument]]] = {
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

    def add_document(self, document: DoorstopDocument) -> None:
        self.data["documents"].append(document)

    def add_item(self, item: DoorstopItem) -> None:
        self.data["items"].append(item)

    def get_items(self) -> list[DoorstopItem]:
        return self.data["items"]

    def get_documents(self) -> list[DoorstopDocument]:
        return self.data["documents"]

    def clear_doc(self, docname: str) -> None:
        self.data["items"] = [
            item for item in self.data["items"] if item.sphinx_doc_name != docname
        ]
        self.data["documents"] = [
            doc for doc in self.data["documents"] if doc.sphinx_doc_name != docname
        ]


def get_document_title(doc: doorstop.Document) -> str:
    if doc._attribute_defaults:
        return doc._attribute_defaults.get("doc", {}).get("title", doc.prefix)
    return doc.prefix


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value(
        "doorstop_root",
        default=".",
        rebuild="env",
        types=[Path],
        description="Root directory of the doorstop tree, relative to the Sphinx conf dir.",
    )
    app.add_domain(DoorstopDomain)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
