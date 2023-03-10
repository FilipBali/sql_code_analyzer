from setuptools import setup, Extension

module = Extension('example', sources=['sql_code_analyzer\\in_memory_representation\\example.pyx'])

setup(
    name='cythonTest',
    version='1.0',
    author='jetbrains',
    ext_modules=[module]
)
