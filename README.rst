============
Introduction
============
This is *Creative Cooking Assistant*, a course project for `CMPS 140/240
(Winter 2011) <http://www.soe.ucsc.edu/classes/cmps140/Winter11/>`_ at UCSC.

------------
Team Members
------------
Graduate Students

- Marcelo Siero
- Gregory Jackson

Undergraduate Students

- Ryan Andonian
- Chris Reynolds
- Andy Nguyen
- Josh Rosen
- Mike Wilson

============
Requirements
============
Our project has been tested with Python 2.6.
Our project requires a few python libraries, which are listed in
``requirements.txt``.  To install the required libraries using `pip
<http://pip.openplans.org/>`_, run ``pip install -r requirements.txt``.
Or run ``sudo make install_requirements``'

The NLG requires Java.

==================
Running the System
==================
To run the command line chat interface, run ``python command_line_interface.py``.
You can also use 'make run'.

The project includes an experimental web server, which can be used by running
``python web_server.py`` and browsing to ``http://localhost:8080``.

Most of these tools accept command line options; try running these programs
with ``--help`` for more information.

To rebuild the database, first import the ontology by running ``python
ontology_import.py``.  Then, use ``python allrecipes.py [filenames of allrecipes
html files]`` to add recipes from allrecipes.com pages.

To update the NLU's ingredients and cuisine wordlists, run ``python
generate_cuisines.py`` and ``python generate_ingredients.py``.
To get a fresh database from the server, rebuild the ingredients, and regenerate
the pickled objects, use ``make refresh``.

================
Coding standards
================

We use the official Python coding standard,
`PEP8 <http://www.python.org/dev/peps/pep-0008/>`_.
The `pep8.py <http://pypi.python.org/pypi/pep8>`_ tool to validate code against
PEP8.  In addition, we use `Pylint <http://www.logilab.org/857>`_ to
perform other code quality checks.  The
included ``pylintrc`` file allows Pylint's checks to be modified as needed.

=======
Testing
=======

In addition to the tests in the ``tests`` directory, some modules contain
`doctests <http://docs.python.org/library/doctest.html>`_.  The doctests in an
individual file can be run using the ``python -m doctest myfilename.py``
command.  Or, `py.test <http://pytest.org/>`_ can run the doctests (in addition
to other tests) using the ``py.test --doctest-modules`` command. Or all tests
can be run by using ``make test``.

The tests directory contains two scripts for evaluating the system.  The
``extract_ingredient_parts_test.py`` tests the ingredient part extraction code
against a number of handwritten examples hosted in a `Google Docs spreadsheet
<https://spreadsheets.google.com/pub?hl=en&hl=en&key=0AvQ9-2eaIan0dHF5QXloVU54SEppamloR2tmRFZlbXc&output=html>`_.
The ``database_stats.py`` script generates statistics on the number of
ingredients, recipes, and ontology nodes in a database and finds ingredients
that are missing from the ontology.
