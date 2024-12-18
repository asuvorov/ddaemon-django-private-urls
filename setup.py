"""(C) 2013-2024 Copycat Software, LLC. All Rights Reserved."""

import os
import re

from os import path
from setuptools import (
    find_packages,
    setup)


PROJECT_PATH = path.abspath(path.dirname(__file__))
VERSION_RE = re.compile(r"""__version__ = [""]([0-9.]+((dev|rc|b)[0-9]+)?)[""]""")


with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as readme:
    README = readme.read()


def get_version():
    """Get Version."""
    with open(path.join(PROJECT_PATH, "privateurl", "__init__.py"), encoding="utf-8") as version:
        init = version.read()

        return VERSION_RE.search(init).group(1)


# -----------------------------------------------------------------------------
# --- Allow `setup.py` to be run from any Path.
# -----------------------------------------------------------------------------
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="ddaemon-django-private-url",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3 License",
    description="Django Private URL",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/asuvorov/ddaemon-django-private-url/",
    author="Artem Suvorov",
    author_email="artem.suvorov@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Plugins",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # "License-Expression: GPL-3.0",
        # "License-File: LICENSE",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Security",
    ],
    install_requires=[],
    test_suite="nose.collector",
    tests_require=["nose"],
)
