import numpy
from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Renderable',
    ext_modules=cythonize("entities/Renderable.py", compiler_directives={"language_level": "3"}),
    include_dirs=[numpy.get_include()],  # Needed if you use NumPy
)