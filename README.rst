DiffuPath |build| |coverage|
==========================

DiffuPath offers a bioinformatic tool foor pathway enrichment, wrapping the generalizable Python implementation diffuPy of the null diffusion algorithm for metabolomics data described by [1]_ and applying it simultaneously over `PathMe <http://networkx.github.io/>`_ [2]_ pathway compilation background network.


Installation
------------
1. ``diffupy`` can be installed with the following commands:

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


Citation
--------
If you use DiffuPath in your work, please cite the R implementation of the null diffusion algorithm [1]_ (more info in `diffuStats <https://github.com/b2slab/diffuStats>`_):

.. [1] Picart-Armada, S., *et al.* (2017). `Null diffusion-based enrichment for metabolomics data <https://doi.org/10.1371/journal.pone.0189012>`_. *PloS one* 12.12.
    
.. [2] Domingo-Fernandez, D., Mubeen, S., Marin-Llao, J., Hoyt, C., & Hofmann-Apitius, M. (2019). `PathMe: Merging and exploring mechanistic pathway knowledge. <https://www.biorxiv.org/content/10.1101/451625v1>`_. *BMC Bioinformatics*, 20:243.

.. |build| image:: https://travis-ci.com/jmarinllao/diffupy.svg?branch=master
    :target: https://travis-ci.com/jmarinllao/diffupy
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/jmarinllao/diffupy/coverage.svg?branch=master
    :target: https://codecov.io/gh/jmarinllao/diffupy?branch=master
    :alt: Coverage Status
