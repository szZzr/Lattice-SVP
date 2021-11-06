#!/bin/bash

mv vm_setup/ ../vm_setup
cd ..
mv vm_setup/Dockerfile Dockerfile
docker image build --cpu-shares=1024 -t svp:latest .
mv Dockerfile vm_setup/Dockerfile
mv vm_setup/ Lattice-SVP/vm_setup