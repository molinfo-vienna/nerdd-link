from setuptools import find_packages, setup

setup(
    name="nerdd-link",
    version="0.4.0",
    maintainer="Steffen Hirte",
    maintainer_email="steffen.hirte@univie.ac.at",
    packages=find_packages(),
    url="https://github.com/molinfo-vienna/nerdd-link",
    description="Run a NERDD module as a Kafka service",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "kafka-python==2.0.2",
        "nerdd-module>=0.3.6",
        "pandas>=1.2.1",
        "pyyaml~=6.0",
        "filetype~=1.2.0",
        "rich-click>=1.7.1",
        "stringcase~=1.2.0",
        "numpy",
        "simplejson>=3",
        "pydantic~=2.9.2",
        # for old Python versions
        "importlib-metadata>=4.6; python_version<'3.10'",
    ],
    extras_require={
        "dev": ["mypy", "ruff"],
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
        "docs": [
            "mkdocs",
            "mkdocs-material",
        ],
    },
    entry_points={
        "console_scripts": [
            "nerdd_job_server = nerdd_link.cli:run_job_server",
            "nerdd_prediction_server = nerdd_link.cli:run_prediction_server",
        ],
    },
)
