#!/bin/bash

./runowning.sh
cd /Lattice-SVP/src
python cython_setup.py build_ext -i
cd /Lattice-SVP
python setup.py develop