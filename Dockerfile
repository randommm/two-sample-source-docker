FROM ubuntu

MAINTAINER Marco Inacio <dockerfiles@marcoinacio.com>
ENV DEBIAN_FRONTEND noninteractive

RUN echo 'Acquire::http { Proxy "http://172.17.0.1:3142"; };' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get dist-upgrade -y && \
    apt-get install -y \
    nano build-essential python3 python3-pip r-base python3-tk && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install npcompare pandas rpy2 pystan matplotlib sklearn

RUN mkdir /workdir
WORKDIR /workdir
ADD files/ /workdir
RUN mkdir plots && mkdir results && mkdir results/metric && \
    mkdir results/mixture

#Set default backend for matplotlib
#Prevents complaing about undefined $DISPLAY
ENV MPLCONFIGDIR /workdir
RUN echo "backend : Agg" > matplotlibrc

RUN R CMD BATCH fourier.R
RUN python3 plot_gaussian_densities.py

RUN python3 runsampler.py type 1
RUN python3 runsampler.py type 2
RUN python3 runsampler.py type 3

RUN python3 runmetric.py type 1 2 & \
    python3 runmetric.py type 1 3 & \
    python3 runmetric.py type 2 3 & \
    python3 runmetric.py type 1 1 & \
    python3 runmetric.py type 2 2 & \
    python3 runmetric.py type 3 3 & \
    wait

RUN python3 runmetric_plots.py

#Dataset with real data used on the article cannot be shared publicly
#Here we are using other dataset with randomly generated data
RUN python3 generate_dataset.py
RUN python3 runsampler.py type real
RUN python3 runmetric.py type real real

CMD tail -F /dev/null
