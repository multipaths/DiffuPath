DiffuPath |build| |docs|
========================
DiffuPath is an analytic tool for biological networks that connects the generic label propagation algorithms from
`DiffuPy <https://github.com/multipaths/DiffuPy/>`_ to biological networks encoded in several formats such as
Simple Interaction Format (SIF) or Biological Expression Language (BEL). For example, in the application scenario
presented in the paper, we use three pathway databases (i.e., KEGG, Reactome and WikiPathways) and their integrated
network retrieved from `PathMe <https://github.com/PathwayMerger/PathMe/>`_ [1]_ to analyze three multi-omics datasets.
However, other biological networks can be imported from the Bio2BEL ecosystem [2]_.

Installation
------------
1. ``diffupath`` can be installed with the following commands:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/multipaths/DiffuPath.git@master

2. or in editable mode with:

.. code-block:: sh

    $ git clone https://github.com/multipaths/DiffuPath.git
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
The following commands can be used directly use from your terminal:

1. **Download a database for network analysis**.

The following command generates a BEL file representing the network of the given database.

.. code-block:: sh

    $ python3 -m diffupath database network --database=<database-name>

To check the available databases, run the following command:

.. code-block:: sh

    $ python3 -m diffupath database ls

2. **Run a diffusion analysis**

The following command will run a diffusion method on a given network with the given data

.. code-block:: sh

    $ python3 -m diffupath diffusion run --network=<path-to-network-file> --input=<path-to-data-file> --method=<method>

Networks
--------
You can choose networks to run diffusion methods in the following ways:

- Select a network representing an individual biological database
- Select multiple databases to generate a harmonized network
- Select from one of four predefined collections of biological databases representing a harmonized network
- Submit your own network from one of the accepted formats

Network Dumps
~~~~~~~~~~~~~
Because of the high computational cost of generating the kernel, we provide links to precalculated kernels for a set of
networks representing biological databases:

- DrugBank [3]_: `drugbank.json <https://drive.google.com/open?id=17azOcU0sstr8DjhvsXQ1XrIY8bqq54lG>`_
- Gene Ontology [4]_: `go.json <https://drive.google.com/open?id=1QeJUQu4nPSGIkKWNErYjf7Eg7eWEBT4J>`_
- HSDN [5]_: `hsdn.json <https://drive.google.com/open?id=18mHVlpoqVmRS13d9UcY9ktWS5e9hU4Ul>`_
- KEGG [6]_: `kegg.json <https://drive.google.com/open?id=13rA2zaoMMf4MVCjZ26fqcUH1PBFgpTDw>`_
- miRTarBase [7]_: `mirtarbase.json <https://drive.google.com/open?id=1Di3myrTX0nQsUtGt9w27yUm7XsDdXnxP>`_
- Reactome [8]_: `reactome.json <https://drive.google.com/open?id=11y_CzI6PZ92NGqvhia-kvSfdexa4rT2Z>`_
- SIDER [9]_: `sider.json <https://drive.google.com/open?id=1fDjpkK6-OuNLAVVfV0OucR466KcMvhST>`_
- WikiPathways [10]_: `wikipathways.json <https://drive.google.com/open?id=1_qVtGfZfV8aB_-R28gkCjjxjYNJmezKP>`_
- Collection #1 (KEGG, Reactome, WikiPathways)
- Collection #2 (KEGG, Reactome, WikiPathways and DrugBank)
- Collection #3 (KEGG, Reactome, WikiPathways, and MirTarBase)

+----------------+------------------------------------------------------------------------+------------+
| Database       | Description                                                            | Reference  |
+================+========================================================================+============+
| DrugBank       | Interactions between drugs and drug targets with over 10,000 drugs     | [3]        |
+----------------+------------------------------------------------------------------------+------------+
| Gene Ontology  | Flexible hierarchy of tens of thousands of biological processes        | [4]        |
+----------------+------------------------------------------------------------------------+------------+
| HSDN           | Associations between thousands of diseases with hundreds of symptoms   | [5]        |
+----------------+------------------------------------------------------------------------+------------+
| KEGG           | Multi-omics interactions present in hundreds of biological pathways    | [6]        |
+----------------+------------------------------------------------------------------------+------------+
| miRTarBase     | Experimentally validated interactions between miRNA and their targets  | [7]        |
+----------------+------------------------------------------------------------------------+------------+
| Reactome       | Multi-omics interactions present in thousands of biological pathways   | [8]        |
+----------------+------------------------------------------------------------------------+------------+
| SIDER          | Associations between over a thousand drugs and side effects            | [9]        |
+----------------+------------------------------------------------------------------------+------------+
| WikiPathways   | Multi-omics interactions present in hundreds of biological pathways    | [10]       |
+----------------+------------------------------------------------------------------------+------------+

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

.. [3] Wishart, D. S., *et al.* (2018). `DrugBank 5.0: a major update to the DrugBank database for 2018
   <https://doi.org/10.1093/nar/gkx1037>`_. Nucleic Acids Research, 46(D1), D1074–D1082.

.. [4] Ashburner, M., *et al.* (2000). `Gene ontology: tool for the unification of biology
   <https://doi.org/10.1038/75556>`_. The Gene Ontology Consortium. Nature Genetics, 25(1), 25–9.

.. [5] Zhou, X., Menche, J., Barabási, A. L., & Sharma, A. (2014). `Human symptoms–disease network
   <https://doi.org/10.1038/ncomms5212>`_. Nature communications, 5(1), 1-10.

.. [6] Kanehisa, *et al.* (2017). `KEGG: new perspectives on genomes, pathways, diseases and drugs.
   <https://doi.org/10.1093/nar/gkw1092>`_. Nucleic Acids Res. 45,D353-D361.

.. [7] Huang, H. Y., *et al.* (2020). `miRTarBase 2020: updates to the experimentally validated microRNA–target
   interaction database <https://doi.org/10.1093/nar/gkz896>`_. Nucleic acids research, 48(D1), D148-D154.

.. [8] Fabregat, A *et al.* (2016). `The Reactome Pathway Knowledgebase <https://doi.org/10.1093/nar/gkv1351>`_. Nucleic
   Acids Research 44. Database issue: D481–D487.

.. [9] Kuhn, M., *et al.* (2016). `The SIDER database of drugs and side effects <https://doi.org/10.1093/nar/gkv1075>`_.
   Nucleic Acids Research, 44(D1), D1075–D1079.

.. [10] Slenter, D.N., *et al.* (2017). `WikiPathways: a multifaceted pathway database bridging metabolomics to other
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
