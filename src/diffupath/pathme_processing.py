# -*- coding: utf-8 -*-

"""This module has utilities methods to mine and retrieve PathMe content."""

import os
from collections import defaultdict

import pybel
from pathme.constants import KEGG_BEL, REACTOME_BEL, WIKIPATHWAYS_BEL
from pybel.constants import ANNOTATIONS
from pybel.dsl import Abundance, BiologicalProcess, CentralDogma, ListAbundance, Reaction


def calculate_database_sets_as_dict(nodes, database):
    """Export as dict databse sets."""
    gene_nodes, mirna_nodes, metabolite_nodes, bp_nodes = calculate_database_sets(nodes, database)
    return {'gene_nodes': gene_nodes,
            'mirna_nodes': mirna_nodes,
            'metabolite_nodes': metabolite_nodes,
            'bp_nodes': bp_nodes}


def get_nodes_in_database(folder):
    """Merge all python pickles in a given folder and returns the corresponding BELGraph."""
    database_networks = [
        pybel.from_pickle(os.path.join(folder, path))
        for path in os.listdir(folder)
        if path.endswith('.pickle')
    ]

    return {
        node
        for network in database_networks
        for node in network.nodes()
    }


def process_reactome_multiple_genes(genes):
    """Process a wrong ID with multiple identifiers."""
    gene_list = []

    for counter, gene in enumerate(genes):

        # Strip the ' gene' prefix
        gene = gene.strip().strip(' gene').strip(' genes')

        # First element is always OK
        if counter == 0:
            gene_list.append(gene)

        # If the identifier starts the same than the first one, it is right
        elif gene[:2] == genes[0][:2]:
            gene_list.append(gene)

        # If the identifier is longer than 2 it is a valid HGNC symbol
        elif len(gene) > 2:
            gene_list.append(gene)

        # If they start different, it might have only a number (e.g., 'ABC1, 2, 3') so it needs to be appended
        elif gene.isdigit():
            gene_list.append(genes[0][:-1] + gene)

        # If the have only one letter (e.g., HTR1A,B,D,E,F,HTR5A)
        elif len(gene) == 1:
            gene_list.append(genes[0][:-1] + gene)

    return gene_list


def munge_reactome_gene(gene):
    """Process/munge Reactome gene."""
    if "," in gene:
        return process_reactome_multiple_genes(gene.split(","))

    elif "/" in gene:
        return process_reactome_multiple_genes(gene.split("/"))

    return gene


def calculate_database_sets(nodes, database):
    """Calculate node sets for each modality in the database."""
    # Entities in WikiPathways that required manual curation
    wikipathways_biol_process = {'lipid biosynthesis', 'hsc survival', 'glycolysis & gluconeogenesis',
                                 'triacylglyceride  synthesis', 'wnt canonical signaling',
                                 'regulation of actin skeleton', 'fatty acid metabolism',
                                 'mrna processing major splicing pathway', 'senescence', 'monocyte differentiation',
                                 'pentose phosphate pathway', 'ethanolamine  phosphate', 'hsc differentiation',
                                 'actin, stress fibers and adhesion', 'regulation of actin cytoskeleton',
                                 's-phase progression', 'g1-s transition', 'toll-like receptor signaling pathway',
                                 'regulation of  actin cytoskeleton', 'proteasome degradation', 'apoptosis',
                                 'bmp pathway', 'ampk activation', 'g1/s checkpoint arrest', 'mapk signaling pathway',
                                 'chromatin remodeling and  epigenetic modifications', 'wnt signaling pathway',
                                 'ros production', 'erbb signaling pathway', 'shh pathway', 'inflammation',
                                 'dna replication', 'mrna translation', 'oxidative stress',
                                 'cell cycle checkpoint activation', 'gi/go pathway', 'wnt pathway',
                                 'g1/s transition of mitotic cell cycle', 'modulation of estrogen receptor signalling',
                                 'dna repair', 'bmp canonical signaling', 'igf and insuline signaling',
                                 'unfolded protein response', 'cell death', 'p38/mapk  pathway', 'glycogen metabolism',
                                 'gnrh signal pathway',
                                 'the intra-s-phase checkpoint mediated arrest of cell cycle progression', 'tca cycle',
                                 'mtor protein kinase signaling pathway', 'proteasome  degradation pathway',
                                 'morphine metabolism', 'hsc aging', 'gastric pepsin release',
                                 'parietal cell production', 'prostaglandin pathway', 'cell cycle (g1/s)  progression',
                                 'notch pathway', 'g2/m progression', 'wnt signaling', 'cell adhesion',
                                 'cell cycle progression', 'egfr pathway', 'cell cycle', 'angiogenesis',
                                 'g2/m-phase checkpoint', 'hsc self renewal', '26s proteasome  degradation',
                                 'mapk signaling', 'immune system up or down regulation', 'm-phase progression',
                                 'insulin signaling', 'nf kappa b pathway', 'cell cycle  progression', 'gi pathway',
                                 'cd45+ hematopoietic-    derived cell    proliferation', "kreb's cycle",
                                 'glycogen synthesis', 'apoptosis pathway', 'g1/s progression',
                                 'inflammasome activation', 'melanin biosynthesis', 'proteasomal degradation',
                                 'g2/m checkpoint arrest', 'g1/s cell cycle transition', 'dna damage response',
                                 'gastric histamine release'}
    wikipathways_metab = {'2,8-dihydroxyadenine', '8,11-dihydroxy-delta-9-thc', 'adp-ribosyl', 'cocaethylene',
                          'dhcer1p', 'ecgonidine', 'f2-isoprostane', 'fumonisins b1', 'iodine', 'l-glutamate',
                          'lactosylceramide', 'methylecgonidine', 'n-acetyl-l-aspartate', 'nad+', 'nadph oxidase',
                          'neuromelanin', 'nicotinic acid (na)', 'nmn', 'pip2', 'sphingomyelin', 'thf'}
    wikipathways_name_normalization = {"Ca 2+": "ca 2+", "acetyl coa": "acetyl-coa", "acetyl-coa(mit)": "acetyl-coa",
                                       "h20": "h2o"}

    # Entities in Reactome that required manual curation
    black_list_reactome = {"5'"}
    reactome_prot = {'phospho-g2/m transition proteins', 'integrin alpha5beta1, integrin alphavbeta3, cd47',
                     'food proteins', 'activated fgfr2', 'adherens junction-associated proteins',
                     'pi3k mutants,activator:pi3k', 'prolyl 3-hydroxylases', 'gpi-anchored proteins', 'c3d, c3dg, ic3b',
                     'c4s/c6s chains', 'activated fgfr1 mutants and fusions', 'activated fgfr3 mutants', 'protein',
                     'cyclin a2:cdk2 phosphorylated g2/m transition protein', 'c4c, c3f', 'activated raf/ksr1',
                     'activated fgfr1 mutants', 'g2/m transition proteins', 'lman family receptors', 'cyclin',
                     'usp12:wdr48:wdr20,usp26', 'proteins with cleaved gpi-anchors', 'activated fgfr2 mutants',
                     'c4d, ic3b', 'c5b:c6:c7, c8, c9', 'cyclin a1:cdk2 phosphorylated g2/m transition protein',
                     'genetically or chemically inactive braf', 'il13-downregulated proteins',
                     'activated fgfr4 mutants', 'rna-binding protein in rnp (ribonucleoprotein) complexes',
                     'effector proteins', 'usp3, saga complex', 'dephosphorylated "receiver" raf/ksr1'}

    gene_nodes = set()
    mirna_nodes = set()
    metabolite_nodes = set()
    bp_nodes = set()

    for node in nodes:

        if isinstance(node, ListAbundance) or isinstance(node, Reaction) or not node.name:
            continue

        # Lower case name and strip quotes or white spaces
        name = node.name.lower().strip('"').strip()

        # Dealing with Genes/miRNAs
        if isinstance(node, CentralDogma):

            ##################
            # miRNA entities #
            ##################

            if name.startswith("mir"):

                # Reactome preprocessing to flat multiple identifiers
                if database == 'reactome':
                    reactome_cell = munge_reactome_gene(name)
                    if isinstance(reactome_cell, list):
                        for name in reactome_cell:
                            mirna_nodes.add(name.replace("mir-", "mir"))
                    else:
                        mirna_nodes.add(name.strip(' genes').replace("mir-", "mir"))

                    continue

                mirna_nodes.add(name.replace("mir-", "mir"))

            ##################
            # Genes entities #
            ##################

            else:
                # Reactome preprocessing to flat multiple identifiers
                if database == 'reactome':
                    reactome_cell = munge_reactome_gene(name)
                    if isinstance(reactome_cell, list):
                        for name in reactome_cell:
                            if name in black_list_reactome:  # Filter entities in black list
                                continue
                            elif name.startswith("("):  # remove redundant parentheses
                                name = name.strip("(").strip(")")

                            gene_nodes.add(name)
                    else:
                        gene_nodes.add(name)
                    continue

                # WikiPathways and KEGG do not require any processing of genes
                if name in wikipathways_biol_process:
                    bp_nodes.add(name)
                    continue
                gene_nodes.add(name)

        #######################
        # Metabolite entities #
        #######################

        elif isinstance(node, Abundance):

            if database == 'wikipathways':
                # Biological processes that are captured as abundance in BEL since they were characterized wrong in WikiPathways
                if name in wikipathways_biol_process:
                    bp_nodes.add(name)
                    continue

                elif node.namespace in {'WIKIDATA', 'WIKIPATHWAYS', 'REACTOME'} and name not in wikipathways_metab:
                    bp_nodes.add(name)
                    continue

                # Fix naming in duplicate entity
                if name in wikipathways_name_normalization:
                    name = wikipathways_name_normalization[name]

            elif database == 'reactome':
                # Curated proteins that were coded as metabolites
                if name in reactome_prot:
                    gene_nodes.add(name)
                    continue

                # Flat multiple identifiers (this is not trivial because most of ChEBI names contain commas,
                # so a clever way to fix some of the entities is to check that all identifiers contain letters)
                elif "," in name and all(
                        string.isalpha()
                        for string in name.split(",")
                ):
                    for string in name.split(","):
                        metabolite_nodes.add(string)
                    continue

            metabolite_nodes.add(name)

        #################################
        # Biological Processes entities #
        #################################

        elif isinstance(node, BiologicalProcess):
            if name.startswith('title:'):
                name = name[6:]  # KEGG normalize

            bp_nodes.add(name)

    return gene_nodes, mirna_nodes, metabolite_nodes, bp_nodes


def get_set_database(database):
    """Return database content subsets by entity for a given db name."""
    if database == 'kegg':
        nodes = get_nodes_in_database(KEGG_BEL)

    if database == 'reactome':
        nodes = get_nodes_in_database(REACTOME_BEL)

    if database == 'wikipathways':
        nodes = get_nodes_in_database(WIKIPATHWAYS_BEL)

    return calculate_database_sets(nodes, database)


def get_labels_by_db_and_omic_from_pathme(databases):
    """Return labels by db and omic from pathme."""
    db_entites = defaultdict(dict)
    entites_db = defaultdict(lambda: defaultdict(set))

    for db in databases:
        genes, mirna, metabolites, bps = get_set_database(db)
        db_entites[db] = {'genes': genes, 'mirna': mirna, 'metabolites': metabolites, 'bps': bps}

        for entity_type, entities in db_entites[db].items():
            entites_db[entity_type][db] = entities

    return db_entites, entites_db


def get_labels_by_db_and_omic_from_graph(graph):
    """Return labels by db and omic given a graph."""
    db_subsets = defaultdict(set)
    db_entites = defaultdict(dict)
    entites_db = defaultdict(dict)

    # entity_type_map = {'Gene':'genes', 'mirna_nodes':'mirna', 'Abundance':'metabolites', 'BiologicalProcess':'bps'}

    for u, v, k in graph.edges(keys=True):
        if ANNOTATIONS not in graph[u][v][k]:
            continue

        if 'database' not in graph[u][v][k][ANNOTATIONS]:
            continue

        for database in graph[u][v][k][ANNOTATIONS]['database']:
            db_subsets[database].add(u)
            db_subsets[database].add(v)

    for database, nodes in db_subsets.items():
        db_entites[database] = calculate_database_sets_as_dict(nodes, database)

        database_sets = calculate_database_sets_as_dict(nodes, database)

        db_entites[database] = database_sets

        for entity_type, entities in database_sets.items():
            entites_db[entity_type][database] = entities

    return db_entites, entites_db
