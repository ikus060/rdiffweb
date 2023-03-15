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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = 'Rdiffweb'
copyright = 'Copyright 2021 Rdiffweb contributors'
author = 'Patrik Dufresne'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    'sphinx.ext.autosectionlabel',
]

autosectionlabel_prefix_document = True

# Enable anchors for cross references
myst_heading_anchors = 2

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
html_theme = 'alabaster'
# Ref: https://alabaster.readthedocs.io/en/latest/customization.html#theme-options
html_theme_options = {
    'description': 'Rdiffweb documentation - A web interface for rdiff-backup',
    'fixed_sidebar': True,
    'caption_font_family': 'Lato,Helvetica,Arial,Verdana,sans-serif',
    'link': '#1c4c72',
    'narrow_sidebar_bg': '#1c4c72',
    'narrow_sidebar_fg': '#fff',
    'narrow_sidebar_link': '#fff',
    'sidebar_header': '#1c4c72',
    'show_powered_by': False,
    'page_width': '1170px',
}
html_show_sourcelink = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
