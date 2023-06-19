#!/usr/bin/env python
"""The setup script."""
from setuptools import find_packages
from setuptools import setup


version = {}
with open("snapchat_dlp/version.py") as fp:
    exec(fp.read(), version)

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = list()

with open("requirements.txt", "r") as file:
    requirements = [r for r in file.readlines() if len(r) > 0]

test_requirements = ["pytest"].extend(requirements)

setup(
    name="snapchat-dlp",
    version=version["__version__"],
    description="An update to snapchat-dlp, a Snapchat Public Stories Downloader.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Walmann/snapchat-dlp",
    author="Aakash Gajjar",
    author_email="skyqutip@gmail.com",
    maintainer="Walmann",
    entry_points={"console_scripts": ["snapchat-dlp=snapchat_dlp.app:main",],},
    include_package_data=True,
    install_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    python_requires=">=3.5",
    keywords="snapchat-dlp",
    license="MIT license",
    packages=find_packages(include=["snapchat_dlp", "snapchat_dlp.*"]),
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
           project_urls={
            'Original': 'https://github.com/skyme5/snapchat-dlp',
            'Source': 'https://github.com/Walmann/snapchat-dlp'
        },
)
