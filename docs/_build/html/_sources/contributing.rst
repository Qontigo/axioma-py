.. _axiomapy-contributing:

Contributing
============

Instructions for Contributors
-----------------------------

Install axioma-py as an editable package.

.. code-block:: bash

    $ pip install -U -e .[test,develop]


Workflow Using GIThub:

1) Clone the axioma-py repository from Github.
2) Create your own branch.  
3) Make changes in your branch. 
4) Run tests to make sure everything works. 
5) Push the branch back to Github.
6) Make a pull request.  

.. code-block:: bash

    $ git checkout -b name_of_your_branch


Edit the files, run tests, format, etc.
Commit to the branch. 
Then push to the remote.

.. code-block:: bash

    git push -u origin <branch>


Then, on the GithHub Project Web page, make the pull request to your branch.


Project Details
------------------

Code is formatted with `black`_ and linted with `flake8`_ (see .flake8 config).

Docstring is Google style.

Type hinting should be used.

A pre-commit config is included to run flake8 before each commit ensuring commits pass linting.
In order to use the hook as defined in the pre-commit-config.yaml run: 

.. code-block:: bash

    pre-commit install

In order to install the package for development, install in editable mode with optional dependencies.

See axioma-py\\examples\\with_entitybase examples for info on how new instances should be defined.

When creating notebook examples or use cases, a git filter is defined (see .gitconfig and .gitattributes files in folders containing notebooks).
The output is automatically removed from notebooks on commit.

Also, any cells tagged 'remove' will be removed on commit. So, for example, credentials can be removed.

A set of scripts is included in ./pre_scripts to help with pre-commit tasks 



Tests
------------

In addition to the coverage tests located in the ./tests, each example notebook from ./examples is converted to a python script and run as part of the pre-commit tests.

See pre_scripts run_all_examples.bat



Building the Docs
-----------------------------

Run either build_docs.bat (Windows CMD) or build_docs.sh (Bash) scripts in the pre_scripts folder.


.. _black: https://pypi.python.org/pypi/black
.. _flake8: https://pypi.org/project/flake8/