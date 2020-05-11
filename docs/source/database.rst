Databases
=========
In this section, we describe the types of networks (databases) you can select to run diffusion methods over. These
include the following and are described in detail in this section [*]_:

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
| DDR            | Disease-disease associations                           | [1]_       | |ddr.json|_                |
+----------------+--------------------------------------------------------+------------+----------------------------+
| DrugBank       | Drug and drug target interactions                      | [2]_       | |drugbank.json|_           |
+----------------+--------------------------------------------------------+------------+----------------------------+
| Gene Ontology  | Hierarchy of tens of thousands of biological processes | [3]_       | |go.json|_                 |
+----------------+--------------------------------------------------------+------------+----------------------------+
| HSDN           | Associations between diseases and symptoms             | [4]_       | |hsdn.json|_               |
+----------------+--------------------------------------------------------+------------+----------------------------+
| KEGG           | Multi-omics interactions in biological pathways        | [5]_       | |kegg.json|_               |
+----------------+--------------------------------------------------------+------------+----------------------------+
| miRTarBase     | Interactions between miRNA and their targets           | [6]_       | |mirtarbase.json|_         |
+----------------+--------------------------------------------------------+------------+----------------------------+
| Reactome       | Multi-omics interactions in biological pathways        | [7]_       | |reactome.json|_           |
+----------------+--------------------------------------------------------+------------+----------------------------+
| SIDER          | Associations between drugs and side effects            | [8]_       | |sider.json|_              |
+----------------+--------------------------------------------------------+------------+----------------------------+
| WikiPathways   | Multi-omics interactions in biological pathways        | [9]_       | |wikipathways.json|_       |
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

You can also take a look at our  `sample networks <https://github.com/multipaths/DiffuPy/tree/master/examples/networks>`_
folder for some examples networks.

References
----------
.. [1] Menche, J., et al. (2015). Disease networks. `Uncovering disease-disease relationships through the incomplete
   interactome <https:doi.org/10.1126/science.1257601>`_. Science, 347(6224), 1257601.

.. [2] Wishart, D. S., *et al.* (2018). `DrugBank 5.0: a major update to the DrugBank database for 2018
   <https://doi.org/10.1093/nar/gkx1037>`_. Nucleic Acids Research, 46(D1), D1074–D1082.

.. [3] Ashburner, M., *et al.* (2000). `Gene ontology: tool for the unification of biology
   <https://doi.org/10.1038/75556>`_. The Gene Ontology Consortium. Nature Genetics, 25(1), 25–9.

.. [4] Zhou, X., Menche, J., Barabási, A. L., & Sharma, A. (2014). `Human symptoms–disease network
   <https://doi.org/10.1038/ncomms5212>`_. Nature communications, 5(1), 1-10.

.. [5] Kanehisa, *et al.* (2017). `KEGG: new perspectives on genomes, pathways, diseases and drugs.
   <https://doi.org/10.1093/nar/gkw1092>`_. Nucleic Acids Res. 45,D353-D361.

.. [6] Huang, H. Y., *et al.* (2020). `miRTarBase 2020: updates to the experimentally validated microRNA–target
   interaction database <https://doi.org/10.1093/nar/gkz896>`_. Nucleic acids research, 48(D1), D148-D154.

.. [7] Fabregat, A *et al.* (2016). `The Reactome Pathway Knowledgebase <https://doi.org/10.1093/nar/gkv1351>`_. Nucleic
   Acids Research 44. Database issue: D481–D487.

.. [8] Kuhn, M., *et al.* (2016). `The SIDER database of drugs and side effects <https://doi.org/10.1093/nar/gkv1075>`_.
   Nucleic Acids Research, 44(D1), D1075–D1079.

.. [9] Slenter, D.N., *et al.* (2017). `WikiPathways: a multifaceted pathway database bridging metabolomics to other
   omics research <https://doi.org/10.1093/nar/gkx1064>`_. *Nucleic Acids Research*, 46(D1):D661-D667.

.. automodule:: diffupath.database
   :members:
