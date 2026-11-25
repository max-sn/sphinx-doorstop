from pathlib import Path
from typing import TYPE_CHECKING, cast

import doorstop
from docutils import nodes
from docutils.parsers.rst import directives
from doorstop import build
from myst_parser.parsers.docutils_ import Parser
from myst_parser.parsers.sphinx_ import MystParser
from sphinx.util.docutils import SphinxDirective, new_document

from sphinx_doorstop.exceptions import SphinxDoorstopError
from sphinx_doorstop.models import SphinxDoorstopDocument, SphinxDoorstopItem
from sphinx_doorstop.utils import get_document_title

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

    from sphinx_doorstop.domain import SphinxDoorstopDomain


class SphinxDoorstopDocumentDirective(SphinxDirective):
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
            raise SphinxDoorstopError(
                f"Failed to build doorstop tree in {doorstop_root}"
            ) from e

        # Try to find the specified document in the tree, but raise an error when it is not found
        try:
            doc = tree.find_document(doc_name)
        except doorstop.common.DoorstopError as e:
            raise SphinxDoorstopError(
                f"Doorstop document {doc_name} not found in {doorstop_root}"
            ) from e

        add_doorstop_files_to_sphinx_rebuild_dependencies(doc, self.env)

        sphinx_doorstop_document = SphinxDoorstopDocument(
            prefix=doc.prefix,
            sphinx_doc_name=self.env.current_document.docname,
            source=doc,
            sep=doc.sep,
        )

        # Use cast to get proper DoorstopDomain type
        domain = cast("SphinxDoorstopDomain", self.env.get_domain("doorstop"))
        domain.add_document(sphinx_doorstop_document)

        # Check if MyST is already being used as parser by the global Sphinx build. If so, use a Sphinx based parser
        # that knows about the included (MyST) extensions. If not, use the default docutils based parser.
        if hasattr(self.env, "myst_config"):
            markdown_parser = MystParser()
        else:
            markdown_parser = Parser()

        return [
            self.create_document_section(
                sphinx_doorstop_document, domain, markdown_parser
            )
        ]

    def create_item_section(
        self,
        item: doorstop.Item,
        domain: "SphinxDoorstopDomain",
        markdown_parser: MystParser | Parser,
    ) -> nodes.section:
        doorstop_item = SphinxDoorstopItem(
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

    def create_document_section(
        self,
        sphinx_doorstop_document: SphinxDoorstopDocument,
        domain: "SphinxDoorstopDomain",
        markdown_parser: MystParser | Parser,
    ) -> nodes.section:
        doc = sphinx_doorstop_document.source
        document_level_section = nodes.section(
            ids=[sphinx_doorstop_document.anchor], names=[doc.prefix]
        )
        document_title = get_document_title(doc)
        target_node = nodes.target("", "", ids=[sphinx_doorstop_document.anchor])
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

        for depth, item_section in item_sections:
            last_section_of_current_level = document_level_section
            for _ in range(depth):
                last_section_of_current_level = last_section_of_current_level.children[
                    -1
                ]
            last_section_of_current_level += item_section

        return document_level_section


def add_doorstop_files_to_sphinx_rebuild_dependencies(
    doc: doorstop.Document, env: "BuildEnvironment"
):
    # Add the document config file to the document dependencies
    env.note_dependency(doc.config)

    # Also add all items to the document dependencies
    for item in doc.items:
        env.note_dependency(item.path)
