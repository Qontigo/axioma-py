.. _axioma-py-examples:

Examples
===================

(The examples notebooks can be downloaded here :download:`all_examples.zip <./attach/all_examples.zip>`)

Instructions for running examples
----------------------------------

Download the zipped set of examples (:download:`all_examples.zip <./attach/all_examples.zip>`) and unzip and cd into that folder.
(Or if you have cloned the repo from GIT, cd to axiomapy/examples)

The examples reference sample data json files and a json from which to load up credentials.  
Two modules are used to load the users and the sample data load_credentials.py and load_sample_data.py.  
In order to run the examples 'as-is' you must create and update the credentials file.


e.g. for Windows using CMD.

.. code-block:: console

    cd credentials
    copy sample.credentials.json credentials.json
    Notepad credentials.json

There are 3 sets of credentials. Only the with_sessions example uses the second and third credentials otherwise only user1 is referenced.
If you do not wish to use the credentials file remove references to load_credentials in the notebook and enter your credentials directly in the notebook.

Sample data is loaded from the files in the /sample_data folder.


The examples are provided as Jupyter Notebooks. 

If you have installed axiomapy in a new environment you may also need to install jupyter.

.. code-block:: bash

    pip install jupyter


Optional: Depending how you launch jupyter you may also need to add a Python Kernel for your new virtual environment which can be selected when running jupyter notebook.

.. code-block:: bash

    ipython kernel install --name "axiomapy-venv-kernel" --user


The start the notebook and open the examples.

.. code-block:: bash

    jupyter notebook





.. toctree::

    Getting Started    <nb_examples/getting_started>
    Sessions    <nb_examples/with_sessions>
    AxiomaAPI    <nb_examples/with_axiomaapi>
    Developer Base Class Guide    <nb_examples/with_entitybase>
