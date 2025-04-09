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
copyright = 'Copyright (C) 2012-2025 rdiffweb contributors'
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

# Did not find an alternative to generate markdown or rst from my spec file.
# Either the solution is obsolete or failing
# So let use this quick and simple solution.
import json

def generate_markdown_from_openapi(openapi_json, output_file):
    """
    Generate a Markdown file from an OpenAPI JSON specification.
    
    :param openapi_json: Path to the OpenAPI JSON file.
    :param output_file: Path to the output Markdown file.
    """
    with open(openapi_json, "r", encoding="utf-8") as f:
        spec = json.load(f)
    
    md_content = []
    
    # Iterate over sorted paths
    md_content.append("# Endpoints")
    for path in sorted(spec.get("paths", {})):
        methods = spec["paths"][path]
        for method, details in methods.items():
            md_content.append(f"\n## {method.upper()} {path}")
            if "description" in details:
                md_content.append(f"**Description:**\n{details['description']}\n")
            
            # Parameters
            parameters = details.get("parameters", [])
            if parameters:
                md_content.append("**Parameters:**")
                for param in parameters:
                    param_name = param.get('name', 'Unnamed')
                    param_in = param.get('in', 'unknown')
                    param_required = " Required" if param.get('required', False) else ""
                    param_default = f" Default: {param.get('default')}" if "default" in param else ""
                    md_content.append(f"- **{param_name}** (in {param_in}){param_required}{param_default}")
                md_content.append("")
            
            # Responses
            md_content.append("**Responses:**")
            for status, response in details.get("responses", {}).items():
                md_content.append(f"- **{status}**: {response.get('description', 'No description')}")
                content = response.get("content", {})
                if content:
                    md_content.append("  - **Content:** " + ", ".join(content.keys()))
    
    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    
    print(f"Markdown documentation generated: {output_file}")

# Example usage
generate_markdown_from_openapi("openapi.json", "endpoints.md")