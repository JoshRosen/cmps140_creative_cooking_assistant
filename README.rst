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
Our project requires a few python libraries, which are listed in
``requirements.txt``.  To install the required libraries using `pip
<http://pip.openplans.org/>`_, run ``pip install -r requirements.txt``.

The NLG requires Java.

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
to other tests) using the ``py.test --doctest-modules`` command.
