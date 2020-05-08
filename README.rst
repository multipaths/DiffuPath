.. image:: https://github.com/multipaths/diffupath/blob/master/docs/source/meta/diffupath_logo.png
   :align: center
   :target: https://diffupath.readthedocs.io/en/latest/

Introduction |build| |docs|
===========================
DiffuPath is an analytic tool for biological networks that connects the generic label propagation algorithms from
`DiffuPy <https://github.com/multipaths/DiffuPy/>`_ to biological networks encoded in several formats such as
Simple Interaction Format (SIF) or Biological Expression Language (BEL). For example, in the application scenario
presented in the paper, we use three pathway databases (i.e., KEGG, Reactome and WikiPathways) and their integrated
network retrieved from `PathMe <https://github.com/PathwayMerger/PathMe/>`_ [1]_ to analyze three multi-omics datasets.
However, other biological networks can be imported from the Bio2BEL ecosystem [2]_.


Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
The latest stable code can be installed from `PyPI <https://pypi.python.org/pypi/diffupath>`_ with:

.. code-block:: sh

   $ python3 -m pip install diffupath

The most recent code can be installed from the source on `GitHub <https://github.com/multipaths/diffupath>`_ with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/multipaths/diffupath.git

For developers, the repository can be cloned from `GitHub <https://github.com/multipaths/diffupath>`_ and installed in
editable mode with:

.. code-block:: sh

   $ git clone https://github.com/multipaths/diffupath.git
   $ cd diffupath
   $ python3 -m pip install -e .

Requirements
------------
``diffupath`` requires the following libraries: ::

    networkx (>=2.1)
    pybel (0.13.2)
    biokeen (0.0.14)
    click (7.0)
    tqdm (4.31.1)
    numpy (1.16.3)
    scipy (1.2.1)
    scikit-learn (0.21.3)
    pandas (0.24.2)
    openpyxl (3.0.2)
    plotly (4.5.3)
    matplotlib (3.1.2)
    matplotlib_venn (0.11.5)
    bio2bel (0.2.1)
    pathme
    diffupy

Command Line Interface
----------------------
The following commands can be used directly from your terminal:

1. **Download a database for network analysis**.

The following command generates a BEL file representing the network of the given database.

.. code-block:: sh

    $ python3 -m diffupath database get-database --database=<database-name>

To check the available databases, run the following command:

.. code-block:: sh

    $ python3 -m diffupath database ls

2. **Run a diffusion analysis**

The following command will run a diffusion method on a given network with the given data

.. code-block:: sh

    $ python3 -m diffupath diffusion diffuse --network=<path-to-network-file> --data=<path-to-data-file> --method=<method>

2. **Run a diffusion analysis**

.. code-block:: sh

    $ python3 -m diffupath diffusion evaluate -i=<input_data> -n=<path_network>

Input Data
----------

You can submit your dataset in any of the following formats:

- CSV (.csv)
- TSV (.tsv)

Please ensure that the dataset minimally has a column 'Node' containing node IDs. You can also optionally add the
following columns to your dataset:

- NodeType
- LogFC [*]_
- p-value

.. [*] |Log| fold change

.. |Log| replace:: Log\ :sub:`2`

Input dataset examples
~~~~~~~~~~~~~~~~~~~~~~

DiffuPath accepts several input formats which can be codified in different ways. See the
`diffusion scores <https://github.com/multipaths/DiffuPy/blob/master/docs/source/diffusion.rst>`_ summary for more
details.

1. You can provide a dataset with a column 'Node' containing node IDs.

+------------+
|     Node   |
+============+
|      A     |
+------------+
|      B     |
+------------+
|      C     |
+------------+
|      D     |
+------------+

2. You can also provide a dataset with a column 'Node' containing node IDs as well as a column 'NodeType', indicating
the entity type of the node to run diffusion by entity type.

+------------+--------------+
|     Node   |   NodeType   |
+============+==============+
|      A     |     Gene     |
+------------+--------------+
|      B     |     Gene     |
+------------+--------------+
|      C     |  Metabolite  |
+------------+--------------+
|      D     |    Gene      |
+------------+--------------+

3. You can also choose to provide a dataset with a column 'Node' containing node IDs as well as a column 'logFC' with
their LogFC. You may also add a 'NodeType' column to run diffusion by entity type.

+--------------+------------+
| Node         |   LogFC    |
+==============+============+
|      A       | 4          |
+--------------+------------+
|      B       | -1         |
+--------------+------------+
|      C       | 1.5        |
+--------------+------------+
|      D       | 3          |
+--------------+------------+

4. Finally, you can provide a dataset with a column 'Node' containing node IDs, a column 'logFC' with their logFC
and a column 'p-value' with adjusted p-values. You may also add a 'NodeType' column to run diffusion by entity type.

+--------------+------------+---------+
| Node         |   LogFC    | p-value |
+==============+============+=========+
|      A       | 4          | 0.03    |
+--------------+------------+---------+
|      B       | -1         | 0.05    |
+--------------+------------+---------+
|      C       | 1.5        | 0.001   |
+--------------+------------+---------+
|      D       | 3          | 0.07    |
+--------------+------------+---------+

You can also take a look at our `sample datasets <https://github.com/multipaths/DiffuPy/tree/master/examples/datasets>`_
folder for some examples files.

Networks
--------
In this section, we describe the types of networks you can select to run diffusion methods over. These include the
following and are described in detail in this section [*]_:

- Select a network representing an individual biological database
- Select multiple databases to generate a harmonized network
- Select from one of four predefined collections of biological databases representing a harmonized network
- Submit your own network [*]_ from one of the accepted formats

.. [*] Please note that all networks available through DiffuPath have been generated using PyBEL v.0.13.2.
.. [*] If there are duplicated nodes in your network, please take a look at this `Jupyter Notebook <https://nbviewer.jupyter.org/github/multipaths/Results/blob/master/notebooks/filter_networks/solve_duplicate_labels_issue.ipynb>`_ to address the issue.

Network Dumps
~~~~~~~~~~~~~
Because of the high computational cost of generating the kernel, we provide links to pre-calculated kernels for a set of
networks representing biological databases.

+----------------+--------------------------------------------------------+------------+----------------------------+
|    Database    |                   Description                          | Reference  |        Download            |
+================+========================================================+============+============================+
| DDR            | Disease-disease associations                           | [3]_       | |ddr.json|_                |
+----------------+--------------------------------------------------------+------------+----------------------------+
| DrugBank       | Drug and drug target interactions                      | [4]_       | |drugbank.json|_           |
+----------------+--------------------------------------------------------+------------+----------------------------+
| Gene Ontology  | Hierarchy of tens of thousands of biological processes | [5]_       | |go.json|_                 |
+----------------+--------------------------------------------------------+------------+----------------------------+
| HSDN           | Associations between diseases and symptoms             | [6]_       | |hsdn.json|_               |
+----------------+--------------------------------------------------------+------------+----------------------------+
| KEGG           | Multi-omics interactions in biological pathways        | [7]_       | |kegg.json|_               |
+----------------+--------------------------------------------------------+------------+----------------------------+
| miRTarBase     | Interactions between miRNA and their targets           | [8]_       | |mirtarbase.json|_         |
+----------------+--------------------------------------------------------+------------+----------------------------+
| Reactome       | Multi-omics interactions in biological pathways        | [9]_       | |reactome.json|_           |
+----------------+--------------------------------------------------------+------------+----------------------------+
| SIDER          | Associations between drugs and side effects            | [10]_      | |sider.json|_              |
+----------------+--------------------------------------------------------+------------+----------------------------+
| WikiPathways   | Multi-omics interactions in biological pathways        | [11]_      | |wikipathways.json|_       |
+----------------+--------------------------------------------------------+------------+----------------------------+

If you would like to use one of our predefined collections, you can similarly download pre-calculated kernels for sets
of networks representing integrated biological databases.

+------------+---------------------------------+-------------------------------------+---------------------------+
| Collection | Database                        | Description                         | Download                  |
+============+=================================+=====================================+===========================+
| #1         | KEGG, Reactome and WikiPathways | -omics and biological               | |pathme.json|_            |
|            |                                 | processes/pathways                  |                           |
+------------+---------------------------------+-------------------------------------+---------------------------+
| #2         | KEGG, Reactome, WikiPathways    | -omics and biological               | |pathme_drugbank.json|_   |
|            | and DrugBank                    | processes/pathways with a strong    |                           |
|            |                                 | focus on drug/chemical interactions |                           |
+------------+---------------------------------+-------------------------------------+---------------------------+
| #3         | KEGG, Reactome, WikiPathways    | -omics and biological processes/    | |pathme_mirtarbase.json|_ |
|            | and MirTarBase                  | pathways enriched with miRNAs       |                           |
+------------+---------------------------------+-------------------------------------+---------------------------+

.. |ddr.json| replace:: ddr.json
.. |drugbank.json| replace:: drugbank.json
.. |go.json| replace:: go.json
.. |hsdn.json| replace:: hsdn.json
.. |kegg.json| replace:: kegg.json
.. |mirtarbase.json| replace:: mirtarbase.json
.. |reactome.json| replace:: reactome.json
.. |sider.json| replace:: sider.json
.. |wikipathways.json| replace:: wikipathways.json
.. |pathme.json| replace:: pathme.json
.. |pathme_drugbank.json| replace:: pathme_drugbank.json
.. |pathme_mirtarbase.json| replace:: pathme_mirtarbase.json

.. _ddr.json: https://drive.google.com/open?id=1inyRVDGNM4XLD0ZxoAT0ekX4WfcBF29H
.. _drugbank.json: https://drive.google.com/open?id=13E1mr0c-aKFaAqAW_8aQglSium0Ji0fp
.. _go.json: https://drive.google.com/open?id=1BzKSShbPMqZQpElVDd-WJGnei_fy94Qg
.. _hsdn.json: https://drive.google.com/open?id=1KSP6lu76jk2B45ShGJEKId8ZkAQCtjHP
.. _kegg.json: https://drive.google.com/open?id=1jiAWFeSxbu4PVApil4jBn7-IzSP5UeCr
.. _mirtarbase.json: https://drive.google.com/open?id=1LNtung6mWp1azqBSx8KKKCzki7M4l--8
.. _reactome.json: https://drive.google.com/open?id=19u1rlhGkN2UACNcMMf6sXyVOzjcVww2t
.. _sider.json: https://drive.google.com/open?id=1izVj2MneOh5y8DHTEaUPGUNgyFdS7MQM
.. _wikipathways.json: https://drive.google.com/open?id=1WUOWsA3dCgDgSsA-N3gXNF7Lb9U1LWdD
.. _pathme.json: https://drive.google.com/open?id=1GnS0BJ7FozPdmPFBJbhBiW-UmfyIgrTW
.. _pathme_drugbank.json: https://drive.google.com/open?id=1jxTBRF3pzhssYpL_3D3Gw46szPnjdSiU
.. _pathme_mirtarbase.json: https://drive.google.com/open?id=1qt_a0R_DpCEBGVXZMywKpr7sKEOShXB3

Custom-network formats
~~~~~~~~~~~~~~~~~~~~~~
You can also submit your own networks in any of the following formats:

- BEL_ (.bel)

- CSV (.csv)

- Edge_ `list`__ (.lst)

- GML_ (.gml or .xml)

- GraphML_ (.graphml or .xml)

- Pickle (.pickle)

- TSV (.tsv)

- TXT (.txt)

.. _Edge: https://networkx.github.io/documentation/stable/reference/readwrite/edgelist.html
__ Edge_
.. _GraphML: http://graphml.graphdrawing.org
.. _BEL: https://language.bel.bio/
.. _GML: http://docs.yworks.com/yfiles/doc/developers-guide/gml.html


Minimally, please ensure each of the following columns are included in the network file you submit:

- Source
- Target

Optionally, you can choose to add a third column, "Relation" in your network (as in the example below). If the relation
between the **Source** and **Target** nodes is omitted, and/or if the directionality is ambiguous, either node can be
assigned as the **Source** or **Target**.


Custom-network example
~~~~~~~~~~~~~~~~~~~~~~

+-----------+--------------+-------------+
| Source    | Target       | Relation    |
+===========+==============+=============+
|     A     |      B       | Increase    |
+-----------+--------------+-------------+
|     B     |      C       | Association |
+-----------+--------------+-------------+
|     A     |      D       | Association |
+-----------+--------------+-------------+

You can also take a look at our `sample networks <https://github.com/multipaths/DiffuPy/tree/master/examples/networks>`_
folder for some examples.


Disclaimer
----------
DiffuPath is a scientific software that has been developed in an academic capacity, and thus comes with no warranty or
guarantee of maintenance, support, or back-up of data.

References
----------
.. [1] Domingo-Fernandez, D., Mubeen, S., Marin-Llao, J., Hoyt, C., *et al.* Hofmann-Apitius, M. (2019). `PathMe:
   Merging and exploring mechanistic pathway knowledge. <https://www.biorxiv.org/content/10.1101/451625v1>`_.
   *BMC Bioinformatics*, 20:243.

.. [2] Hoyt, C. T., *et al.* (2019). `Integration of Structured Biological Data Sources using Biological Expression
   Language <https://doi.org/10.1101/631812>`_. *bioRxiv*, 631812.

.. [3] Menche, J., et al. (2015). Disease networks. `Uncovering disease-disease relationships through the incomplete
   interactome <https:doi.org/10.1126/science.1257601>`_. Science, 347(6224), 1257601.

.. [4] Wishart, D. S., *et al.* (2018). `DrugBank 5.0: a major update to the DrugBank database for 2018
   <https://doi.org/10.1093/nar/gkx1037>`_. Nucleic Acids Research, 46(D1), D1074–D1082.

.. [5] Ashburner, M., *et al.* (2000). `Gene ontology: tool for the unification of biology
   <https://doi.org/10.1038/75556>`_. The Gene Ontology Consortium. Nature Genetics, 25(1), 25–9.

.. [6] Zhou, X., Menche, J., Barabási, A. L., & Sharma, A. (2014). `Human symptoms–disease network
   <https://doi.org/10.1038/ncomms5212>`_. Nature communications, 5(1), 1-10.

.. [7] Kanehisa, *et al.* (2017). `KEGG: new perspectives on genomes, pathways, diseases and drugs.
   <https://doi.org/10.1093/nar/gkw1092>`_. Nucleic Acids Res. 45,D353-D361.

.. [8] Huang, H. Y., *et al.* (2020). `miRTarBase 2020: updates to the experimentally validated microRNA–target
   interaction database <https://doi.org/10.1093/nar/gkz896>`_. Nucleic acids research, 48(D1), D148-D154.

.. [9] Fabregat, A *et al.* (2016). `The Reactome Pathway Knowledgebase <https://doi.org/10.1093/nar/gkv1351>`_. Nucleic
   Acids Research 44. Database issue: D481–D487.

.. [10] Kuhn, M., *et al.* (2016). `The SIDER database of drugs and side effects <https://doi.org/10.1093/nar/gkv1075>`_.
   Nucleic Acids Research, 44(D1), D1075–D1079.

.. [11] Slenter, D.N., *et al.* (2017). `WikiPathways: a multifaceted pathway database bridging metabolomics to other
   omics research <https://doi.org/10.1093/nar/gkx1064>`_. *Nucleic Acids Research*, 46(D1):D661-D667.

.. |build| image:: https://travis-ci.com/multipaths/diffupath.svg?branch=master
    :target: https://travis-ci.com/multipaths/diffupath
    :alt: Build Status

.. |docs| image:: http://readthedocs.org/projects/diffupath/badge/?version=latest
    :target: https://diffupath.readthedocs.io/en/latest/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/gh/multipaths/diffupath/coverage.svg?branch=master
    :target: https://codecov.io/gh/multipaths/diffupath?branch=master
    :alt: Coverage Status

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/diffupath.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/diffupath.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/diffupath.svg
    :alt: Apache-2.0

