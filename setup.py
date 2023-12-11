from setuptools import find_packages, setup

# some RDKit versions are not recognized by setuptools
# -> check if RDKit is installed by attempting to import it
# -> if RDKit can be imported, do not add it to install_requires
rdkit_installed = False
try:
    import rdkit

    rdkit_installed = True
except ModuleNotFoundError:
    pass

# rdkit 2022.3.3 is the oldest (reasonable) version
rdkit_requirement = ["rdkit>=2022.3.3"] if not rdkit_installed else []

setup(
    name="nerdd-kafka",
    version="0.1.0",
    maintainer="Steffen Hirte",
    maintainer_email="steffen.hirte@univie.ac.at",
    packages=find_packages(),
    url="https://github.com/molinfo-vienna/nerdd-kafka",
    description="Run a NERDD module as a Kafka service",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=rdkit_requirement
    + [
        "kafka-python==2.0.2",
        "pandas>=1.2.1",
        "pyyaml~=6.0",
        "filetype~=1.2.0",
        "rich-click>=1.7.1",
        "stringcase~=1.2.0",
    ],
    extras_require={
        "dev": [],
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "pytest-bdd",
            "pytest-mock",
            "pytest-watch",
            "hypothesis",
            "hypothesis-rdkit",
        ],
    },
    entry_points={
        "console_scripts": [
            "run_nerdd_server = nerdd_kafka.__main__:main",
        ],
    },
)
