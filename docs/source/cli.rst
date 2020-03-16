Command Line Interface
======================
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

.. click:: diffupath.cli:main
   :prog: diffupath
   :show-nested:
