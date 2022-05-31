.. axioma-py documentation master file, created by
   sphinx-quickstart on Fri Jun 12 14:58:10 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================
Welcome to axioma-py
=====================


**axioma-py** is a Python software development kit (SDK) created for Qontigo customers and partners. It is a set 
of Python wrappers for our Axioma REST API that provide easy access to its endpoints. It supports Python versions 
3.6 and above. 



Key Features
============

- Offers a more intuitive interface for users less familiar with the API and its data models.
- Provides async support for relevant methods.
- Allows developers to work with dict representations alongside typed instances where this is more convenient.
- Improves the developer and API user’s experience.
- Comes fully documented with tutorials and examples and packaged with more boilerplate code to reduce time needed to build applications.
- Provides clear design to allow collaboration.
- Discusses advanced applications and use cases.



Library Installation
====================


Requirements:

- Python 3.6 or greater
- Access to PIP package manager

If you don't already have one, create a virtualenv using `these instructions <https://docs.python.org/3/library/venv.html>`_ from the official Python documentation. Per the instructions, "it is always recommended to use a virtualenv while developing Python applications."

Clone the axioma-py repository in your local system from Github.

Once the package is available in your local, install the package to use it as a utility in your virtual environment. To install the package use the pip command from inside the package:

.. code-block:: console

    $ pip install -U -e .[test,develop]


Now the package is ready to use.

Getting Started and Examples
=============================

Head to the :ref:`Examples <axioma-py-examples>` pages to get started.


Contributing
==============

See the Contributing guide :ref:`instructions for contributors <axiomapy-contributing>` for details.


Table Of Contents
=================

.. toctree::
   :maxdepth: 1
   :caption: Examples and Use Cases:

   examples2

.. toctree::
   :maxdepth: 2
   :caption: Packages:

   sessions
   axiomapyapi
   odatafilterhelpers


.. toctree::
   :maxdepth: 2
   :caption: Other:

   contributing
   changelog



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _venv_link https://docs.python.org/3/library/venv.html