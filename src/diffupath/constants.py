"""Constants of DiffuPath."""

import os


from diffupy.constants import METHODS

dir_path = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIR = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)))

#: Default DiffuPath directory
DEFAULT_DIFFUPATH_DIR = os.path.join(os.path.expanduser('~'), '.diffupath')

#: Default DiffuPath output directory
OUTPUT_DIFFUPATH_DIR = os.path.join(DEFAULT_DIFFUPATH_DIR, 'output')

ROOT_RESULTS_DIR = os.path.join(os.path.abspath(os.path.join(SOURCE_DIR, os.pardir)))
ROOT_RESULTS_DIR = os.path.join(os.path.abspath(os.path.join(ROOT_RESULTS_DIR, os.pardir)))
ROOT_RESULTS_DIR = os.path.join(ROOT_RESULTS_DIR, 'Results')

OUTPUT_DIR = os.path.join(ROOT_RESULTS_DIR, 'outputs')

HSA = 'Homo_sapiens'

def ensure_output_dirs():
    """Ensure that the output directories exists."""
    os.makedirs(DEFAULT_DIFFUPATH_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


ensure_output_dirs()

"""Available diffusion cross-validation methods"""

#: raw
BY_METHOD = 'method'
BY_DB = 'database'
LTOO = 'ltoo'

BY_ENTITY = 'entity'
BY_ENTITY_METHOD = 'by_entity_method'
BY_ENTITY_DB = 'by_entity_db'

EVALUATION_COMPARISONS = {
    LTOO,
    BY_METHOD,
    BY_DB,
    BY_ENTITY,
    BY_ENTITY_METHOD,
    BY_ENTITY_DB
}

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

DATABASE_LINKS = {
    'ddr': '1inyRVDGNM4XLD0ZxoAT0ekX4WfcBF29H',
    'drugbank': '13E1mr0c-aKFaAqAW_8aQglSium0Ji0fp',
    'gene_ontology': '1BzKSShbPMqZQpElVDd-WJGnei_fy94Qg',
    'hsdn': '1KSP6lu76jk2B45ShGJEKId8ZkAQCtjHP',
    'kegg': '1jiAWFeSxbu4PVApil4jBn7-IzSP5UeCr',
    'mirtarbase': '1LNtung6mWp1azqBSx8KKKCzki7M4l--8',
    'reactome': '19u1rlhGkN2UACNcMMf6sXyVOzjcVww2t',
    'sider': '1izVj2MneOh5y8DHTEaUPGUNgyFdS7MQM',
    'wikipathways': '1WUOWsA3dCgDgSsA-N3gXNF7Lb9U1LWdD',
    'pathme': '1WUOWsA3dCgDgSsA-N3gXNF7Lb9U1LWdD',
    'pathme_drugbank': '1jxTBRF3pzhssYpL_3D3Gw46szPnjdSiU',
    'pathme_mirtarbase': '1qt_a0R_DpCEBGVXZMywKpr7sKEOShXB3',
}



PATHME_DRUGBANK=frozenset(['kegg', 'reactome', 'wikipathways'])
PATHME_MIRTARBASE=frozenset(['kegg', 'reactome', 'wikipathways'])
PATHME_DB=frozenset(['kegg', 'reactome', 'wikipathways'])

PATHME_MAPPING = {
    PATHME_DB: 'pathme',
    PATHME_DRUGBANK:'pathme_drugbank',
    PATHME_MIRTARBASE:'pathme_mirtarbase',
}
