# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import axiomapy

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(1, os.path.abspath("../"))
print(sys.path)

# -- Project information -----------------------------------------------------


release = axiomapy.__version__


project = "axiomapy"
copyright = "2024 Axioma by SimCorp"
author = "Axioma"

# The full version, including alpha/beta/rc tags


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.coverage",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "sphinx_copybutton",  # for "copy to clipboard" buttons
    "enum_tools.autoenum",
]


autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": False,
    "autoclass_content": "class",
    "autosummary_generate": True,
}

autosummary_generate = True

# using rinoh for pdf
rinoh_documents = [
    (
        "index",  # top-level file (index.rst)
        "bluepytoolkit",  # output (target.pdf)
        "Documentation",  # document title
        "Axioma",
    )
]  # document author

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for nbsphinx output -------------------------------------------------
html_sourcelink_suffix = ""
mathjax_config = {
    "TeX": {"equationNumbers": {"autoNumber": "AMS", "useLabelIds": True}},
}
nbsphinx_execute = "never"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"https://docs.python.org/": None}
