project = "clr-loader"
copyright = "2022, Benedikt Reinartz"
author = "Benedikt Reinartz"

extensions = ["sphinx.ext.autodoc"]

# Add parent to path for autodoc
import sys, os

sys.path.append(os.path.abspath(".."))

# autodoc_typehints = "both"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
html_static_path = []
