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

sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "src")))

version = "master"

# -- Project information -----------------------------------------------------

project = "yadg"
copyright = "2021 - 2022, yadg authors"
author = "Peter Kraus"
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "sphinxcontrib.autodoc_pydantic"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_css_files = [
    "custom_theme.css",
]
html_theme_options = {
    "body_max_width": "none",
    "sticky_navigation": True,
    "navigation_depth": 6
}
html_logo = "./images/yadg.png"
html_favicon = "./images/yadg_ico.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["images", "_static"]


# -- Extension configuration -------------------------------------------------
show_authors = True
autosummary_generate = False
autodoc_default_flags = ["members", "undoc-members", "show-inheritance"]
autodoc_member_order = "bysource"
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_member_order = "bysource"

autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_member_order = "bysource"
intersphinx_mapping = {
    'dgbowl_schemas': ("https://dgbowl.github.io/dgbowl-schemas/master", None)
}