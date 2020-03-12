"""Constants of DiffuPath."""

import os

from diffupy.constants import METHODS

dir_path = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIR = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)))

#: Default DiffuPath directory
DEFAULT_DIFFUPY_DIR = os.path.join(os.path.expanduser('~'), '.diffupath')
#: Default DiffuPath output directory
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
#: KEGG
KEGG_NAME = 'kegg'
#: Reactome
REACTOME_NAME = 'reactome'
#: WikiPathways
WIKIPATHWAYS_NAME = 'wikipathways'

# Complementary databases from Bio2BEL
#: MirTarBase
MIRTARBASE_NAME = 'mirtarbase'
#: SIDER
SIDER_NAME = 'sider'
#: PhewasCatalog
PHEWAS_NAME = 'phewascatalog'
#: HSDN
HSDN_NAME = 'hsdn'
#: DDR
DDR_NAME = 'ddr'
#: DrugBank
DRUGBANK_NAME = 'drugbank'
#: Gene Ontology
GENE_ONTOLOGY_NAME = 'go'

#: Databases available for download in DiffuPath
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

#: DiffuPath available network formats
FORMATS = [
    CSV,
    TSV,
    GRAPHML,
    BEL,
    NODE_LINK_JSON,
    BEL_PICKLE,
]

#: Separators
FORMAT_SEPARATOR_MAPPING = {
    CSV: ',',
    TSV: '\t'
}

"""Acceptable column names of user submitted network"""

#: Column name for source node
SOURCE = 'source'
#: Column name for target node
TARGET = 'target'
#: Column name for relation
RELATION = 'relation '
