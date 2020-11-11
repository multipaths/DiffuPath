BASIC USAGE
===========
The main required input to run diffusion using *DiffuPath* is:
 1) A **network/graph**. (see Network-Input Formatting below)
 2) A **dataset of scores**. (see Scores-Input Formatting below)

.. image:: meta/DiffuPyScheme2.png
  :width: 400
  :alt: Alternative text

For its usability, you can either:

 - Use the `Command Line Interface (see cli) <https://github.com/multipaths/DiffuPath/blob/master/docs/source/cli.rst>`_.
 - Use *pythonically* the **functions** provided in *diffupath.cli*:

.. code-block:: python3

  from diffupath.cli import run

  # DATA INPUT and GRAPH as PATHs -> returned as *Pandas DataFrame*
  diffusion_scores = run('~/data/input_scores.csv', '~/data/network.csv').as_pd_dataframe()

  # DATA INPUT and GRAPH as Python OBJECTS -> exported *as_csv*
  diffusion_scores = run(input_scores, network).as_csv('~/output/diffusion_results.csv')

.. automodule:: diffupath.cli.run
   :members:

Customization
~~~~~~~~~~~~~

Network
-------
You can customize the *PathMe* background network:

- Constructing it by selecting among the available `Biological Network Databases (see database) <https://github.com/multipaths/DiffuPath/blob/master/docs/source/database.rst>`_.
- Filtering the default network either **by database** or **by omic**.

.. code-block:: python3

  diffusion_scores = run(input_scores, filter_network_database = ['KEGG'], filter_network_omic = ['gene', 'mirna'])

If you wish to use your own network, we recommend you to check the supported formats in `DiffuPy <https://github.com/multipaths/DiffuPy/blob/master/docs/source/usage.rst>`_
and directly use DiffuPy, since *DiffuPath* wraps it to offer diffusion with the *PathMe* environment networks.

Methods
-------
The diffusion method by default is *z*, which statistical normalization has previously shown outperformance over raw
diffusion [1]. Further parameters to adapt the propagation procedure are also provided, such as choosing among the
available diffusion methods or providing a custom method function. See the `diffusion Methods and/or Method modularity <https://github.com/multipaths/DiffuPy/blob/master/docs/source/diffusion.rst>`_.

.. code-block:: python3

  diffusion_scores_select_method = run(input_scores, method = 'raw')

  from networkx import page_rank # Custom method function

  diffusion_scores_custom_method = run(input_scores, method = page_rank)

You can also provide your own kernel method or select among the ones provided in *kernels.py* function which you can
provide as a *kernel_method* argument. By default *regularised_laplacian_kernel* is used.

.. code-block:: python3

  from diffupath.kernels import p_step_kernel # Custom kernel calculation function

  diffusion_scores_custom_kernel_method = run(input_scores, method = 'raw', kernel_method = p_step_kernel)

So *method* stands for the **diffusion process** method, and *kernel_method* for the **kernel calculation** method.

FORMATTING
==========

Before running diffusion using *DiffuPath*, take into account the **input data/scores formats**.
You can find specified here samples of supported input scores.

If you wish to use your own network, we recommend you to check the supported formats in `DiffuPy <https://github.com/multipaths/DiffuPy/blob/master/docs/source/usage.rst>`_
and directly use DiffuPy, since *DiffuPath* wraps it to offer diffusion with the *PathMe* environment networks.

Input format
~~~~~~~~~~~~~

The input is preprocessed and further mapped before the diffusion. See input mapping or or `see process_input docs <https://github.com/multipaths/DiffuPy/blob/master/docs/source/preprocessing.rst>`_ in *DiffuPy* for further details.
Here are exposed the covered input formats for its preprocessing.

Scores
--------
You can submit your dataset in any of the following formats:

- CSV (*.csv*)
- TSV (*.tsv*)
- *pandas.DataFrame*
- *List*
- *Dictionary*

(check Input dataset examples)

So you can **either** provide a **path** to a *.csv* or *.tsv* file:

.. code-block:: python3

  from diffupath.cli import run

  diffusion_scores_from_file = run('~/data/diffusion_scores.csv')

or **Pythonically** as a data structure as the *input_scores* parameter:

.. code-block:: python3

  data = {'Node':  ['A', 'B',...],
        'Node Type': ['Metabolite', 'Gene',...],
         ....
        }
  df = pd.DataFrame (data, columns = ['Node','Node Type',...])

  diffusion_scores_from_dict = run(df)


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
details on how the labels input are treated according to each available method.

**1.** You can provide a dataset with a column 'Node' containing node IDs.

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

.. code-block:: python3

  from diffupath.cli import run

  diffusion_scores = run(dataframe_nodes)

Also as a list of nodes:

.. code-block:: python3

  ['A', 'B', 'C', 'D']

.. code-block:: python3

  diffusion_scores = run(['A', 'B', 'C', 'D'])


**2.** You can also provide a dataset with a column 'Node' containing node IDs as well as a column 'NodeType',
indicating the entity type of the node to run diffusion by entity type.

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

Also as a dictionary of type:list of nodes :

.. code-block:: python3

  {'Gene': ['A', 'B', 'D'], 'Metabolite': ['C']}

.. code-block:: python3

  diffusion_scores = run({'Genes': ['A', 'B', 'D'], 'Metabolites': ['C']}, network)


**3.** You can also choose to provide a dataset with a column 'Node' containing node IDs as well as a column 'logFC'
with their logFC. You may also add a 'NodeType' column to run diffusion by entity type.

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

Also as a dictionary of node:score_value :

.. code-block:: python3

  {'A':-1, 'B':-1, 'C':1.5, 'D':4}

.. code-block:: python3

  diffusion_scores = run({'A':-1, 'B':-1, 'C':1.5, 'D':4})

Combining point 2., you can also indicating the node type:

+--------------+------------+--------------+
| Node         |   LogFC    |   NodeType   |
+==============+============+==============+
|      A       | 4          |     Gene     |
+--------------+------------+--------------+
|      B       | -1         |     Gene     |
+--------------+------------+--------------+
|      C       | 1.5        |  Metabolite  |
+--------------+------------+--------------+
|      D       | 3          |    Gene      |
+--------------+------------+--------------+

Also as a dictionary of type:node:score_value :

.. code-block:: python3

  {Gene: {A:-1, B:-1, D:4}, Metabolite: {C:1.5}}

  diffusion_scores = run({Gene: {A:-1, B:-1, D:4}, Metabolite: {C:1.5}}, network)


**4.** Finally, you can provide a dataset with a column 'Node' containing node IDs, a column 'logFC' with their logFC
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

This only accepted pythonicaly in dataaframe format.

See the `sample datasets <https://github.com/multipaths/DiffuPy/tree/master/examples/datasets>`_ directory for example
files.


Input Mapping/Coverage
~~~~~~~~~~~~~~~~~~~~~~
Even though it is not relevant for the input user usage, taking into account the input mapped entities over the
background network is relevant for the diffusion process assessment, since the coverage of the input implies the actual
entities-scores that are being diffused. In other words, only the entities whose labels match an entity in the network
will be further processed for diffusion.

Running diffusion will report the mapping as follows:

.. code-block:: RST

   Mapping descriptive statistics

   wikipathways:
   gene_nodes  (474, 0.1538961038961039)
   mirna_nodes  (2, 0.046511627906976744)
   metabolite_nodes  (12, 0.75)
   bp_nodes  (1, 0.004464285714285714)
   total  (489, 0.14540588760035683)

   kegg:
   gene_nodes  (1041, 0.337987012987013)
   mirna_nodes  (3, 0.06976744186046512)
   metabolite_nodes  (6, 0.375)
   bp_nodes  (12, 0.05357142857142857)
   total  (1062, 0.3157894736842105)

   reactome:
   gene_nodes  (709, 0.2301948051948052)
   mirna_nodes  (1, 0.023255813953488372)
   metabolite_nodes  (6, 0.375)
   total  (716, 0.22809812042051608)

   total:
   gene_nodes  (1461, 0.4344335414808207)
   mirna_nodes  (4, 0.0011894142134998512)
   metabolite_nodes  (13, 0.003865596193874517)
   bp_nodes  (13, 0.003865596193874517)
   total  (1491, 0.4433541480820696)

To graphically see the mapping coverage, you can also plot a `heatmap view of the mapping (see views) <https://github.com/multipaths/DiffuPath/blob/master/docs/source/views.rst>`_.
To see how the mapping is performed over a input pipeline preprocessing, take a look at this `Jupyter Notebook <https://nbviewer.jupyter.org/github/multipaths/Results/blob/master/notebooks/processing_datasets/dataset_1.ipynb>`_
or `see process_input docs <https://github.com/multipaths/DiffuPy/blob/master/docs/source/preprocessing.rst>`_ in
*DiffuPy*.

Output format
~~~~~~~~~~~~~
The returned format is a custom *Matrix* type, with node labels as rows and a column with the diffusion score, which can
be exported into the following formats:

.. code-block:: python3

  diffusion_scores.to_dict()
  diffusion_scores.as_pd_dataframe()
  diffusion_scores.as_csv()
  diffusion_scores.to_nx_graph()


References
----------
.. [1] Picart-Armada, S., *et al.* (2017). `Null diffusion-b
