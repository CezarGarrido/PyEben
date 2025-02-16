from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "dataflex_converter",
        ["dataflex_converter.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++"
    )
]

setup(
    name="dataflex_converter",
    version="1.0",
    ext_modules=ext_modules
)
