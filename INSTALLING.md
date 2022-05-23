
# Installation and Setup

axioma-py is a Python software development kit (SDK) created for Qontigo customers and partners. It can be used to import portfolios and data, perform complex risk and attribution analysis, and generate reports or other output.


## Who is this For?


This is for clients and prospects of Qontigo who would prefer to use a python-based code to access our rest API. It assumes a working knowledge of python. It includes instructions on how to download and set up the project in a local system and some additional items you may need to set this up to work offline. 


## Installation Prerequisites

* If you don't already have one, create a virtualenv using [these instructions](https://docs.python.org/3/library/venv.html) from the official Python documentation.  Per the instructions, "It is always recommended to use a virtualenv while developing Python applications."

* In order to install the package for development, install in editable mode with optional dependencies. See the "with_entitybase" examples in the [examples](axiomapy/examples) folder for info on how new instances should be defined.



## Scripts

A set of scripts is included in the [pre_scripts](pre_scripts) folder to help with pre-commit tasks.


## Tests  

There are coverage tests located in the [test](axiomapy/test) subdirectory.



## Downloading, Configuring Python, and Important File Locations

Perform a Git checkout of the **master** branch of the project. It contains the most recent code. **git checkout -b <branch_name>** will create a new branch and switch to it at the same time (a separate branch is an essential prerequisite for contributing).

* The code is formatted with black and linted with flake8 (see .flake8 config).

* Docstring is Google style.

* Type hinting should be used.

* A pre-commit config is included to run flake8 before each commit ensuring commits pass linting.

* Install axioma-py as an editable package:


   ```
        $ pip install -U -e .[test,develop]
   ```

* In your project checkout, see **...\examples\with_entitybase** examples for information on how new instances should be defined. 

* When creating notebook examples or use cases, a git filter is defined (see **gitconfig** and **gitattributes** files).

*  The output is automatically removed from notebooks on commit (see the **.gitconfig** and the **.gitattributes** files in folders containing notebooks.) Also, any cells tagged 'remove' will be removed on commit, so, for example, credentials can be removed.

* A set of scripts is included in the **./pre_scripts** directory to help with pre-commit tasks.


## Can I see some examples of current code?

You can find some examples [here](/axiomapy/examples). In addition, the documents linked in the Documentation section, below, provide detailed annotated code examples.


## Where is the Documentation?

The documentation and examples can be accessed directly on the GitHub website [here, in the html folder](docs/_build/html), should you want to browse before downloading the project.  The axioma-py package uses Sphinx to auto-generate documentation.  The guide comes with a detailed hyperlinked index, useful for finding information quickly.


### Generating the Documentation in Your Downloaded Project 


While the documentation is pre-built, if you have added code and documented it similarly to the code comments used in the rest of the project, you may want to rebuild the documentation and review the formatted results in the User Guide. To build the documents offline into a formatted online manual, run `build-docs.bat` (for Windows) and `build_docs_no_check.sh` (for Unix/Linux) in the pre_scripts folder of the project.  

* You will need to install Sphinx in order to work with the documentation.

* Navigate to the pre_scripts directory, and execute **build_docs.bat**.
 
* When the html documents are built, navigate in your local checkout to the built documents folder, for example: **bluepysdk-package\docs\_build\html**.  

* Double-click **index.html** to open the online help to the contents page. 

The online help manual reads like a standard user's guide, and the numerous "source" links in it take you directly to an example of the code being described by the documentation. These code examples are stored in subdirectories in the html directory. They are not the original code.


## Thank You!

Thank you again for reviewing this project. If you have any comments or suggestions, or are just curious, we'd love hearing from you.  Please contact us at <axioma-py@qontigo.com> and put "axioma-py" in the subject line.  

--*The axioma-py Team*


