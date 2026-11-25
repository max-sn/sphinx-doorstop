Reference
=========

Configuration
-------------

.. confval:: doorstop_root
    :type: ``str | Path``

    The root directory of the Doorstop tree. Relative to Sphinx's 'conf.py'
    file. Default ``"."``.

.. confval:: doorstop_custom_attribute_name_map
    :type: ``dict[str, str] | None``

    A dictionary that maps custom attribute names to publish names. For example::

        doorstop_custom_attribute_name_map = {"invented-by": "Author"}

    If an attribute name is not present in the dictionary this is logged as a warning.

    If omitted or set to ``None``, a default formatter will be used that replaces separators with spaces and capitalizes
    the name. The used function is shown below.

    .. literalinclude:: ../../src/sphinx_doorstop/directives.py
        :pyobject: default_custom_attribute_formatter

    If it is set to ``{}``, the default formatter is not used, and missing attribute names are not logged as warning.

Directives
----------

.. rst:directive:: .. doorstop:document:: <prefix>

    Include all items from a document with ``<prefix>``.

    .. rst:directive:option:: numbered

        Add the `Doorstop item level`_ as heading number for every item in this
        document.

.. _Doorstop item level: https://doorstop.readthedocs.io/en/latest/reference/item.html#level
