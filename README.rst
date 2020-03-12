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


Network Dumps
-------------
Because it is high computational cost of generating the kernel, we provide links to precalculated kernels for some of
the networks representing biological databases:

- KEGG [3]_:
- Reactome [4]_:
- WikiPathways [5]_:

Disclaimer
----------
DiffuPath is a scientific software that has been developed in an academic capacity, and thus comes with no warranty or
guarantee of maintenance, support, or back-up of data.

References
----------
.. [1] Domingo-Fernandez, D., Mubeen, S., Marin-Llao, J., Hoyt, C., & Hofmann-Apitius, M. (2019). `PathMe: Merging and exploring mechanistic pathway knowledge. <https://www.biorxiv.org/content/10.1101/451625v1>`_. *BMC Bioinformatics*, 20:243.

.. [2] Hoyt, C. T., *et al.* (2019). `Integration of Structured Biological Data Sources using Biological Expression Language
       <https://doi.org/10.1101/631812>`_. *bioRxiv*, 631812.

.. [3] Kanehisa, *et al.* (2017). `KEGG: new perspectives on genomes, pathways, diseases and drugs. <https://doi.org/10.1093/nar/gkw1092>`_. Nucleic Acids Res. 45,
       D353-D361.

.. [4] Fabregat, A *et al.* (2016). `The Reactome Pathway Knowledgebase <https://doi.org/10.1093/nar/gkv1351>`_. Nucleic Acids Research 44. Database issue:
       D481–D487.

.. [5] Slenter, D.N., *et al.* (2017). `WikiPathways: a multifaceted pathway database bridging metabolomics to other omics
       research <https://doi.org/10.1093/nar/gkx1064>`_. *Nucleic Acids Research*, 46(D1):D661-D667.

.. |build| image:: https://travis-ci.com/multipaths/diffupath.svg?branch=master
    :target: https://travis-ci.com/multipaths/diffupath
    :alt: Build Status

.. |docs| image:: http://readthedocs.org/projects/diffupath/badge/?version=latest
    :target: https://diffupath.readthedocs.io/en/latest/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/gh/multipaths/diffupath/coverage.svg?branch=master
    :target: https://codecov.io/gh/multipaths/diffupath?branch=master
    :alt: Coverage Status
