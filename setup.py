import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = "atuproot",
    version = "0.1.13",
    author = "Shane Breeze",
    author_email = "sdb15@ic.ac.uk",
    scripts = [],
    description = "AlphaTwirl + uproot = FAST analysis code",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/shane-breeze/atuproot",
    download_url = "https://github.com/shane-breeze/atuproot/archive/0.1.13.tar.gz",
    packages = setuptools.find_packages(),
    install_requires = ["six", "numpy", "alphatwirl>=0.20.1", "uproot>=2.9.7"],
    setup_requires = ["pytest-runner"],
    tests_require = ["pytest"],
    classifiers = (
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
    ),
)
