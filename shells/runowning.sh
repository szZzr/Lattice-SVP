#!/bin/bash

chown --reference=/Lattice-SVP/src/Lattice_SVP/worker/worker_process/__init__.py /Lattice-SVP/src/Lattice_SVP/worker/worker_process/WorkerProcess.pyx
chown --reference=/Lattice-SVP/src/Lattice_SVP/manager/manager_process/__init__.py /Lattice-SVP/src/Lattice_SVP/manager/manager_process/ManagerProcess.pyx
chown --reference=/Lattice-SVP/src/Lattice_SVP/worker/__init__.py /Lattice-SVP/src/Lattice_SVP/worker/__main__.py
chown --reference=/Lattice-SVP/src/Lattice_SVP/manager/__main__.py /Lattice-SVP/src/Lattice_SVP/manager/manager.py
chown --reference=/Lattice-SVP/src/Lattice_SVP/pot/pot.py /Lattice-SVP/src/Lattice_SVP/pot/__main__.py
chown --reference=/Lattice-SVP/src/Lattice_SVP/pot/pot.py /Lattice-SVP/src/Lattice_SVP/pot/__init__.py


