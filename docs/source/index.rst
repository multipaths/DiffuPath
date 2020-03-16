DiffuPath
=========
DiffuPath is an analytic tool for biological networks that connects the generic label propagation algorithms from
`DiffuPy <https://github.com/multipaths/DiffuPy/>`_ to biological networks encoded in several formats such as
Simple Interaction Format (SIF) or Biological Expression Language (BEL). For example, in the application scenario
presented in the paper, we use three pathway databases (i.e., KEGG, Reactome and WikiPathways) and their integrated
network retrieved from `PathMe <https://github.com/PathwayMerger/PathMe/>`_ [1]_ to analyze three multi-omics datasets.
However, other biological networks can be imported from the Bio2BEL ecosystem [2]_.

Installation is as easy as getting the code from `PyPI <https://pypi.python.org/pypi/diffupath>`_ with
:code:`python3 -m pip install diffupath`. See the :doc:`installation <installation>` documentation.

.. seealso::

    - Documented on `Read the Docs <http://diffupath.readthedocs.io/>`_
    - Versioned on `GitHub <https://github.com/multipaths/diffupath>`_
    - Tested on `Travis CI <https://travis-ci.org/multipaths/diffupath>`_
    - Distributed by `PyPI <https://pypi.python.org/pypi/diffupath>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   cli
   constants
   database
   cross_validation
   views
   pathme_processing
   topological_analyses
   input_mapping


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
