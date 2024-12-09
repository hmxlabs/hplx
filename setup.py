from setuptools import setup 
from setuptools import find_namespace_packages

setup(
    
    name = "hmxlabs.hplx",
    version = "1.0.0",
    py_modules= ['hmxlabs.hplx.hplx'],
    packages = find_namespace_packages('src')
)