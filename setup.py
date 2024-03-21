import setuptools
import versioneer

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()

with open("README.md", "r", encoding="utf-8") as infile:
    readme = infile.read()

packagedir = "src"

setuptools.setup(
    name="yadg",
    version=version,
    cmdclass=cmdclass,
    author="Peter Kraus",
    author_email="peter@tondon.de",
    description="yet another datagram",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/dgbowl/yadg",
    project_urls={
        "Bug Tracker": "https://github.com/dgbowl/yadg/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": packagedir},
    packages=setuptools.find_packages(where=packagedir),
    python_requires=">=3.9",
    install_requires=[
        "numpy~=1.23",
        "scipy~=1.9",
        "pint~=0.20",
        "pyyaml~=6.0",
        "uncertainties~=3.1",
        "striprtf~=0.0.22",
        "tzlocal~=4.2",
        "packaging~=21.3",
        "python-dateutil~=2.8.2",
        "openpyxl~=3.0.10",
        "requests~=2.28",
        "dgbowl-schemas==116",
        "pydantic~=2.0",
    ],
    extras_require={
        "testing": ["pytest"],
        "docs": [
            "sphinx==4.5.0",
            "sphinx-rtd-theme",
            "sphinx-autodoc-typehints",
            "autodoc-pydantic",
        ],
    },
    entry_points={"console_scripts": ["yadg=yadg:run_with_arguments"]},
)
