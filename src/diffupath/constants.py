"""Constants of DiffuPath."""

import os

from diffupy.constants import METHODS

dir_path = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIR = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)))

DEFAULT_DIFFUPY_DIR = os.path.join(os.path.expanduser('~'), '.diffupath')
OUTPUT_DIR = os.path.join(DEFAULT_DIFFUPY_DIR, 'output')


def ensure_output_dirs():
    """Ensure that the output directories exists."""
    os.makedirs(DEFAULT_DIFFUPY_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


ensure_output_dirs()

# Rename DiffuPy methods
DIFFUPY_METHODS = METHODS
EMOJI = "🌐"

# Available databases from PathMe
KEGG_NAME = 'kegg'
REACTOME_NAME = 'reactome'
WIKIPATHWAYS_NAME = 'wikipathways'

# Complementary databases from Bio2BEL
MIRTARBASE_NAME = 'mirtarbase'
SIDER_NAME = 'sider'
PHEWAS_NAME = 'phewascatalog'
HSDN_NAME = 'hsdn'
DDR_NAME = 'ddr'
DRUGBANK_NAME = 'drugbank'
GENE_ONTOLOGY_NAME = 'go'

DATABASES = [
    KEGG_NAME,
    REACTOME_NAME,
    WIKIPATHWAYS_NAME,
    MIRTARBASE_NAME,
    SIDER_NAME,
    PHEWAS_NAME,
    HSDN_NAME,
    DDR_NAME,
    DRUGBANK_NAME,
    GENE_ONTOLOGY_NAME,
]

"""Available formats"""

CSV = 'csv'
TSV = 'tsv'
GRAPHML = 'graphml'
BEL = 'bel'
NODE_LINK_JSON = 'json'
BEL_PICKLE = 'pickle'
GRAPHML = 'graphml'
GML = 'gml'

FORMATS = [
    CSV,
    TSV,
    GRAPHML,
    BEL,
    NODE_LINK_JSON,
    BEL_PICKLE,
]
