#!/usr/bin/env python

import os

from setuptools import find_packages, setup

VERSION = os.getenv("CI_COMMIT_TAG")
if not VERSION:
    VERSION = "0.0.1"

# --- >
setup(
    name="skill-newyear-quest",
    version=VERSION,
    package_dir={"skill_newyear_quest": "src/skill_newyear_quest"},
    python_requires=">=3.6",
    packages=find_packages(where="src", include=["skill_newyear_quest"]),
    url="https://gitlab.com/nickandreevart/skill_newyear_quest",
    license="MIT",
    author="n.andreev",
    author_email="nickandreevart@gmail.com",
    description="skill-newyear-quest",
)

