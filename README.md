Source code for article "Comparing two populations using Bayesian Fourier series density estimation".

Usage
-----

You can install all dependencies and run all simulation by building the Dockerfile with:
::

    docker build -t yourbuildname .

You can then run a container and copy the contents of /workdir to some folder on your computer:
::

    docker run --rm -d yourbuildname | xargs -I {} bash -c "docker cp {}:/workdir /somefolder && docker stop {}"
