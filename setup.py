"""Setup script for jvcli."""

import os

from setuptools import find_packages, setup


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
    author="TrueSelph Inc.",
    author_email="admin@trueselph.com",
    packages=find_packages(
        include=["jvcli", "jvcli.*"],
    ),
    include_package_data=True,
    install_requires=[
        "click>=8.1.8",
        "requests>=2.32.3",
        "packaging>=24.2",
        "pyaml>=25.1.0",
        "jac-cloud>=0.1.19",
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
