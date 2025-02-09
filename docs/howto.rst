How To - Project Documentation
======================================================================

Get Started
----------------------------------------------------------------------

Documentation can be written as rst files in `scaleos/docs`.


To build and serve docs, use the commands::

    docker compose -f docker-compose.local.yml up docs



Changes to files in `docs/_source` will be picked up and reloaded automatically.

`Sphinx <https://www.sphinx-doc.org/>`_ is the tool used to build documentation.

Docstrings to Documentation
----------------------------------------------------------------------

The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ is used to automatically document code using signatures and docstrings.

Numpy or Google style docstrings will be picked up from project files and available for documentation. See the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension for details.

For an in-use example, see the `page source <_sources/users.rst.txt>`_ for :ref:`users`.

To compile all docstrings automatically into documentation source files, use the command:
    ::

        make apidocs


This can be done in the docker container:
    ::

        docker run --rm docs make apidocs

Solve `polymorphic_ctype_id` value defined..

The model AgePriceMatrix# **1** does not have a `polymorphic_ctype_id` value defined.
Where the number after the # is the id of the given content type.
    ::

        AgePriceMatrix.objects.filter(id=1).update(polymorphic_ctype_id=ContentType.objects.filter(model__iexact="AgePriceMatrix").first().id)

Generate a key pair for Django WebPush:
    ::

        https://pypi.org/project/django-webpush/
        https://web-push-codelab.glitch.me/