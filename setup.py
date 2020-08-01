"""
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
"""

from setuptools import setup, find_packages  # type: ignore
from distutils.util import convert_path
from codecs import open
import os
from typing import Any, Dict

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

const_data: Dict[str, Any] = {}
ver_path = convert_path("fbarber/const.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), const_data)

setup(
    name="fastx-barber",
    version=const_data["__version__"],
    description="FASTX trimming tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ggirelli/fast-barber",
    author="Gabriele Girelli",
    author_email="gabriele.girelli@scilifelab.se",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="bioinformatics fasta fastq trimming",
    packages=find_packages(),
    install_requires=["biopython==1.77", "regex==2020.7.14", "tqdm==4.48.0"],
    scripts=[],
    entry_points={"console_scripts": ["fbarber = fbarber.scripts.barber:main"]},
    test_suite="nose.collector",
    tests_require=["nose"],
)
