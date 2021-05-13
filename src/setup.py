# Project       : BlockChain
# Script        : core.py
# Author        : ParisNeo (Saifeddine ALOUI)
# Description   : The setup file for building the library using python


from pathlib import Path
from typing import Union

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_requirements(path: Union[str, Path]):
    with open(path, "r") as file:
        return file.read().splitlines()


requirements = read_requirements("requirements.txt")
requirements_dev = read_requirements("requirements_dev.txt")

setuptools.setup(
    name="blockchain",
    version="0.0.1",
    author="ParisNeo",
    author_email="aloui.saifeddine@gmail.com",
    description="A block chain code for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ParisNeo/blockchain",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)