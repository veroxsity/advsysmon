#!/usr/bin/env python3
"""
Setup script for Advanced System Monitor
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
install_requires = [
    "psutil>=5.9.0",
    "rich>=13.0.0",
    "colorama>=0.4.6",
    "tabulate>=0.9.0",
    "blessed>=1.19.1",
    "click>=8.1.0",
]

# Optional dependencies for GPU monitoring
extras_require = {
    "gpu": ["pynvml>=11.5.0", "GPUtil>=1.4.0"],
    "all": ["pynvml>=11.5.0", "GPUtil>=1.4.0"],
}

setup(
    name="advanced-sysmon",
    version="1.0.0",
    author="Daniel",
    author_email="veroxsity@gmail.com",
    description="A feature-rich, modern system monitor with beautiful terminal UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/veroxsity/advsysmon",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "advanced-sysmon=advanced_sysmon.core:main",
        ],
    },
    keywords="system monitor cpu memory disk network process terminal ui rich",
    project_urls={
        "Bug Reports": "https://github.com/veroxsity/advsysmon/issues",
        "Source": "https://github.com/veroxsity/advsysmon",
        "Documentation": "https://github.com/veroxsity/advsysmon#readme",
    },
)
