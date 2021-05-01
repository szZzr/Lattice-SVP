import os, numpy, json
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

#---User Defined Options---
# index = 'worker'


with open("../system_paths.json","r") as f:
    system_paths = json.load(f)

# c_path= '/usr/local/Cellar/gcc/10.2.0_2/bin/g++-10'

os.environ["CC"] = system_paths['g++']
os.environ["CXX"] = system_paths['g++']

file_names = {'manager': 'ManagerProcess',
            'worker': 'WorkerProcess'}
dir_paths = {'manager':'Lattice_SVP/manager/manager_process/',
             'worker':'Lattice_SVP/worker/worker_process/'}


ext = lambda index: Extension(
    dir_paths[index].replace('/','.') + file_names[index],
    [dir_paths[index] + file_names[index]+'.pyx'],
    language='c++',
    libraries=['MyTool', 'zmq','boost_serialization'],
    library_dirs=["cpp_Lattice_SVP/libs",
                  # "/usr/local/Cellar/zeromq/4.3.2/lib",
                  # "/usr/local/Cellar/boost/1.72.0_1/lib"
                  system_paths['zmq']['lib'],
                  system_paths['boost']['lib']
                  ],
    include_dirs=["cpp_Lattice_SVP/include",
                  # "/usr/local/Cellar/zeromq/4.3.2/include",
                  # "/usr/local/Cellar/boost/1.72.0_1/include"
                  system_paths['zmq']['include'],
                  system_paths['boost']['include']
                  ],
    extra_compile_args=['-std=c++17'],#'-fopenmp', "-Os","-fPIC"
    #extra_link_args=['-fopenmp']
)

setup(
    #name=file_name,
    cmd_class={'build_ext': build_ext},
    ext_modules=cythonize([ext(index) for index in file_names.keys()]),
    include_dirs=[numpy.get_include(),"."]
)


# In order to recognize Cython's module by python class, should instantiate
# as package, the directory of compilation result ".so" . So that, it invokes
# the supbrocess to create an empty __init__.py to convert the directory to package.
import subprocess
for index in file_names.keys():
    subprocess.run(['touch',dir_paths[index] + '__init__.py'])

#compile command: > python setup.py build_ext -i
