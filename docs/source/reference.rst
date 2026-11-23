Reference
=========

Configuration
-------------

.. confval:: doorstop_root

    The root directory of the Doorstop tree. Relative to Sphinx's 'conf.py'
    file.

Directives
----------

.. rst:directive:: .. doorstop:document:: <prefix>

    Include all items from a document with ``<prefix>``.

    .. rst:directive:option:: numbered

        Add the `Doorstop item level`_ as heading number for every item in this
        document.

.. _Doorstop item level: https://doorstop.readthedocs.io/en/latest/reference/item.html#level
