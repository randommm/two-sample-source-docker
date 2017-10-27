Source code for article "Comparing two populations using Bayesian Fourier series density estimation".

Usage
-----

You can install all dependencies by building the Dockerfile with:
::

    docker build -t yourbuildname .

You can then run run all simulation by starting a container:
::

    FOLDER_TO_STORE_RESULTS="$HOME/results_bfs"
    docker run --rm -it -v $FOLDER_TO_STORE_RESULTS:/workdir yourbuildname

Where $FOLDER_TO_STORE_RESULTS is the local folder where the results will be stored.

You can also use the pre-builded version available directly on Docker Hub:
::

    FOLDER_TO_STORE_RESULTS="$HOME/results_bfs"
    docker run --rm -it -v $FOLDER_TO_STORE_RESULTS:/workdir marcoinacio/two-sample-source-docker
