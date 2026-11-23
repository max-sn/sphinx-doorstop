Quickstart
==========

Start with an existing Doorstop project, or follow along the steps below to
create one. If you already have a Doorstop project, go to `Configure Sphinx`_.

Create a Doorstop project
-------------------------

Initialize a `Doorstop <https://doorstop.readthedocs.io/>`__ project with
Markdown with ``doorstop create``, e.g.:

.. code-block:: shell

    cd docs/design
    doorstop create --digits 2 --itemformat markdown UC ./use-cases

Optionally, create a non-normative item that can represent a document
introduction with ``doorstop add``, e.g.:

.. code-block:: shell

    doorstop add UC --number 0

Update the contents of ``./use-cases/UC00.md`` to resemble:

.. literalinclude:: ../design/use-cases/UC00.md
    :language: markdown
    :emphasize-lines: 6, 11-13

Create a (normative) item with ``doorstop add``, e.g.:

.. code-block:: shell

    doorstop add UC

.. tip::

    Add the ``--edit`` command line option to automatically open it in your
    preferred editor.

Add a header and text:

.. literalinclude:: ../design/use-cases/UC01.md
    :language: markdown
    :emphasize-lines: 11-13

Now you have a very basic Doorstop document that you can include in your Sphinx
build.

Configure Sphinx
----------------

Install the extension with your preferred package manager::

    pip install sphinx-doorstop
    poetry add sphinx-doorstop
    uv add sphinx-doorstop

Add the extension to ``conf.py``::

    extensions = [
        ...
        "sphinx_doorstop",
    ]

Configure where your document tree can be found::

    # -- Options for sphinx-doorstop ---------------------------------------------

    doorstop_root = "../design"

Add the :rst:dir:`doorstop:document` somewhere in your Sphinx source files:

.. code-block:: rst

    .. doorstop:document:: UC
        :numbered:

Example
-------

The result will approximately be:

.. doorstop:document:: UC
    :numbered:
