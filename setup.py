import setuptools

with open("README.md", "r", encoding="utf-8") as infile:
    readme = infile.read()

packagedir = "src"

setuptools.setup(
    name = "yadg",
    version = "3.0.7",
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
        'uncertainties'
    ],
    entry_points = {
        "console_scripts": [
            'yatest=yadg.test_yadg:main',
            'yadg=yadg.yadg:main'
        ]
    }
)