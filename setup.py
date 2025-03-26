#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for AI Influencer System
"""

import os
import sys
from setuptools import setup, find_packages

# Read the README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ai_influencer",
    version="1.0.0",
    author="Manus AI",
    author_email="user@example.com",
    description="AI Influencer system for automated content posting on platform X",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai_influencer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tweepy",
        "openai",
        "pillow",
        "matplotlib",
        "requests",
        "schedule",
        "PyQt5",
        "python-dotenv",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "ai_influencer=ai_influencer.main:main",
        ],
    },
)
