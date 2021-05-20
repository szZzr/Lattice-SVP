#!/bin/bash

mkdir ../instructions
mv install-dependencies.sh ../instructions/install-dependencies.sh
mv requires.txt ../instructions/requires.txt
mv Dockerfile ../Dockerfile
cd ..
docker image build -t svp:latest .