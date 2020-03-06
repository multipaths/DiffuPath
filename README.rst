DiffuPath |build| |docs| |coverage|
===================================

DiffuPath is an analytic tool for biological networks that connects the generic label propagation algorithms from  `DiffuPy <https://github.com/multipaths/DiffuPy/>`_ to biological networks encoded in Biological Expression Language (BEL). For example, in the application scenario presented in the paper, we use three pathway databases (i.e., KEGG, Reactome and WikiPathways) and their integrated network retrieved from `PathMe <https://github.com/PathwayMerger/PathMe/>`_ [1]_ to analyze three multi-omics datasets. However, other biological networks can be imported from the Bio2BEL ecosystem [2]_.

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

How to Use
----------

1. **Generate Kernel**

Generates the kernel of a given BEL graph.

.. code-block:: sh

    $ python3 -m diffupath kernel


References
----------
.. [1] Domingo-Fernandez, D., Mubeen, S., Marin-Llao, J., Hoyt, C., & Hofmann-Apitius, M. (2019). `PathMe: Merging and exploring mechanistic pathway knowledge. <https://www.biorxiv.org/content/10.1101/451625v1>`_. *BMC Bioinformatics*, 20:243.

.. [2] Hoyt, C. T., *et al.* (2019). `Integration of Structured Biological Data Sources using Biological Expression Language
       <https://doi.org/10.1101/631812>`_. *bioRxiv*, 631812.
       
Disclaimer
----------
DiffuPath is a scientific software that has been developed in an academic capacity, and thus comes with no warranty or guarantee of maintenance, support, or back-up of data.

.. |build| image:: https://travis-ci.com/multipaths/diffupath.svg?branch=master
    :target: https://travis-ci.com/multipaths/diffupath
    :alt: Build Status
    
.. |docs| image:: http://readthedocs.org/projects/diffupath/badge/?version=latest
    :target: https://diffupath.readthedocs.io/en/latest/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/gh/multipaths/diffupath/coverage.svg?branch=master
    :target: https://codecov.io/gh/multipaths/diffupath?branch=master
    :alt: Coverage Status
