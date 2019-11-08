import setuptools

import engine

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bcompiler-engine",
    version=engine.__version__,
    author="Matthew Lemon",
    author_email="matt@matthewlemon.com",
    description="Library for parsing spreadsheets using datamaps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hammerheadlemon/bcompiler-engine",
    packages=setuptools.find_packages(),
    install_requires=[
        "openpyxl",
        "appdirs"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ]
)
