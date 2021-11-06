FROM ubuntu:latest
#
# MetaData
#
LABEL author='Giorgos'
LABEL maintainer='sizorcsd@hotmail.gr'
LABEL description='Shortest Vector Problem via Lattice'
RUN apt-get update && apt-get upgrade -y
#
# Installation of Python3.6
#
RUN apt-get install -y --no-install-recommends  software-properties-common && \
	apt-get update && add-apt-repository ppa:deadsnakes/ppa -y && \
	apt-get update && apt-get install -y python3.6
#
# Installation of GCC-COMPILER
#
RUN apt-get update && \
	apt-get install -y --no-install-recommends build-essential && \
	add-apt-repository ppa:ubuntu-toolchain-r/test && \
	apt-get update && apt-get install -y --no-install-recommends gcc-10 g++-10
#
# Installation for requirements libraries for FPLLL lib
#
RUN apt-get install -y --no-install-recommends \
	libgmp3-dev libmpfr-dev libmpc-dev \
	libtool autoconf pkg-config fplll-tools
#
# Installation for requirements libraries for cpp-modules
#
RUN apt-get install -y --no-install-recommends \
	libzmq3-dev libboost-all-dev libomp5 libomp-dev
#
# Installation of FPLLL, FPYLLL and python's necessary libraries
#
RUN ln -sf /bin/python3.6 /bin/python && \
	ln -sf /bin/python3.6 /bin/python3 && \
	apt-get update && \
	apt-get install -y python3-pip libpython3.6-dev git
#
# Setting System's PATHs
#
ENV PKG_CONFIG_PATH="/usr/lib/x86_64-linux-gnu"
ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/local/lib:/usr/lib:/lib"
ENV PATH="$PATH:/usr/lib"
#
# Import instructions and Install Libraries via repo Requirements
#
COPY vm_setup/instructions ./instructions
RUN instructions/install-dependencies.sh
RUN pip install -r instructions/requires.txt
#
# Import REPO
#
COPY Lattice-SVP ./Lattice-SVP
#
# Compile CPP-Modules
#
WORKDIR /Lattice-SVP/src/cpp_Lattice_SVP/include
RUN mkdir ../libs && make
#
# Compile Cython-Modules
#
WORKDIR /Lattice-SVP/src
RUN python cython_setup.py build_ext -i
#
# Install Lattice-SVP Package
#
WORKDIR /Lattice-SVP
RUN python setup.py develop