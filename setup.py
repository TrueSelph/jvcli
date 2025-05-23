"""Setup script for jvcli."""

import os

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version() -> str:
    """Get the package version from the __init__ file."""
    version_file = os.path.join(os.path.dirname(__file__), "jvcli", "__init__.py")
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Version not found.")


setup(
    name="jvcli",
    version=get_version(),
    description="CLI tool for Jivas Package Repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TrueSelph Inc.",
    author_email="admin@trueselph.com",
    url="https://github.com/TrueSelph/jvcli",
    packages=find_packages(
        include=["jvcli", "jvcli.*"],
    ),
    include_package_data=True,
    package_data={
        "jvcli": ["client/**/*"],
    },
    install_requires=[
        "click>=8.1.8",
        "requests>=2.32.3",
        "packaging>=24.2",
        "pyaml>=25.1.0",
        "jac-cloud==0.1.20",
        "streamlit>=1.42.0",
        "streamlit-elements>=0.1.0",
        "streamlit-router>=0.1.8",
        "streamlit-javascript>=0.1.5",
        "python-dotenv>=1.0.0",
        "semver>=3.0.4",
        "node-semver>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pre-commit",
            "pytest",
            "pytest-mock",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "jvcli = jvcli.cli:jvcli",
        ],
    },
    python_requires=">=3.12",
)
