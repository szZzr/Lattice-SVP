from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import os, numpy

# import subprocess
# subprocess.call(["cython","-a","C2_SchnorrEuchner.pyx"])


# for macOS: setup gcc-compiler!
os.environ["CC"] = "../venv/gcc_osx/9.3.0/bin/gcc-9"
os.environ["CXX"] = "../venv/gcc_osx/9.3.0/bin/gcc-9"

extensions = [Extension(
    # 'test2',
    # ['test2.pyx'],
    'C2_SchnorrEuchner',
    ['C2_SchnorrEuchner.pyx'],
    language='c',
    # annotate=True
    # extra_compile_args=['-fopenmp', "-Os"],
    # extra_link_args=['-fopenmp']
)]

setup(
    # name='test2',
    name = 'C2_SchnorrEuchner',
    cmd_class={'build_ext': build_ext},
    ext_modules=cythonize(extensions),
    include_dirs=[numpy.get_include()]
)
