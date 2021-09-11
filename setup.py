import setuptools
import os

with open(os.path.join("src", "yadg", "helpers", "version.py")) as code:
    exec(code.read())
print(_VERSION)

with open("README.md", "r", encoding="utf-8") as infile:
    readme = infile.read()

packagedir = "src"

setuptools.setup(
    name = "yadg",
    version = _VERSION,
    author = "Peter Kraus",
    author_email = "peter@tondon.de",
    description = "Yet Another DataGram",
    long_description = readme,
    long_description_content_type = "text/markdown",
    url = "https://github.com/PeterKraus/yadg",
    project_urls = {
        "Bug Tracker": "https://github.com/PeterKraus/yadg/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": packagedir},
    packages = setuptools.find_packages(where = packagedir),
    python_requires = ">=3.6",
    install_requires = [
        'matplotlib',
        'numpy',
        'scipy',
        'uncertainties',
        'peakutils'
    ],
    entry_points = {
        "console_scripts": [
            'yadg=yadg.yadg:main',
            'dg2json=yadg.dg2json:main',
            'dg2png=yadg.dg2png:main'
        ]
    }
)
