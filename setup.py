"""
setup.py - Package setup for App Trace Cleaner
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="app-trace-cleaner",
    version="1.0.0",
    author="App Trace Cleaner",
    description="Safe, intelligent Windows application leftover cleaner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "app-trace-cleaner=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
