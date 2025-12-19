from setuptools import setup, find_packages
import os

# Get the directory where setup.py is located
setup_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="meta-repo-cli",
    version="0.1.0",
    description="Meta-repo CLI for system orchestration",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "PyYAML>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "meta=meta.cli:main",
        ],
    },
    python_requires=">=3.8",
)

