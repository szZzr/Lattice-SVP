from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Lattice_SVP',
    version='0.1',
    description='This package tries to solve the SVP Problem,\
                applies Lattice-Techniques. The solution based \
                on Schnorr and Euchner Enumeration algorithm. \
                This package constitutes a parallel and distributed \
                implementation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/szZzr/Lattice-SVP',
    author='szZzr',
    author_email='sizorcsd@hotmail.gr',
    license='MIT',
    packages= find_packages(where = 'src',
                            include = ['Lattice_SVP','simulator']),
    package_dir = {'':'src'},
    package_data = {
        'data':["*"]
    },
    entry_points = {'console_scripts':[
                'simulator = simulator.__main__:main',
                'manager = Lattice_SVP.manager.__main__:manager',
                'worker = Lattice_SVP.worker.__main__:main',
                'pot = Lattice_SVP.pot.__main__:main']},
    install_requires=['autoconf','cysignals','clang','Cython','pycrypto','gmpy2',
                      'numpy','fpylll','intel-openmp','janus', 'setuptools','pyzmq',
                      'janus'],
    extras_requires = ['colorama','style','update'],
    #test_suite='tests',
    zip_safe = False
    )


# python setup.py sdist --manifest-only
# # -o is a shortcut for --manifest-only.
