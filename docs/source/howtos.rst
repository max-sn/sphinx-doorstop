How to's
========

Add a custom title to the document
----------------------------------

The default title for a document is the prefix specified as argument to
:rst:dir:`doorstop:document`. You can change this by changing the
`attributes.defaults.doc.title` field in the document's index YAML file
(``.doorstop.yml``). For example:

.. code-block:: yaml

    settings:
      digits: '2'
      itemformat: markdown
      prefix: UC
      sep: ''
    attributes:
      defaults:
        doc:
          title: "Use cases"

Include Mermaid diagrams
------------------------

By default, the `MyST docutils parser`_ is used to process the Markdown contents
of the item text.

*Sphinx doorstop* detects whether your Sphinx project is already using the MyST
parser extension, and uses the `MyST Sphinx parser`_ instead. That also enables
using any directive known to Sphinx in the Markdown contents of the Doorstop
items.

To render Mermaid diagrams, use the excellent `sphinxcontrib-mermaid`_
extension. Instead of using directive fences:

.. code-block::

    ```{mermaid}
    <diagram contents>
    ```

You can set ``myst_fence_as_directive = ["mermaid"]`` and use:

.. code-block::

    ```mermaid
    <diagram contents>
    ```

.. _MyST docutils parser: https://myst-parser.readthedocs.io/en/latest/apidocs/myst_parser/myst_parser.parsers.docutils_.html#myst_parser.parsers.docutils_.Parser
.. _MyST Sphinx parser: https://myst-parser.readthedocs.io/en/latest/apidocs/myst_parser/myst_parser.parsers.sphinx_.html#myst_parser.parsers.sphinx_.MystParser
.. _sphinxcontrib-mermaid: https://sphinxcontrib-mermaid-demo.readthedocs.io/en/latest/index.html
