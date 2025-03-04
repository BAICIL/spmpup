# setup.py

from setuptools import setup, find_packages

setup(
    name="spmpup",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "spmpup": ["data/*.nii.gz", "data/*.txt"],
    },
    author="Dhruman Goradia",
    author_email="Dhruman.Goradia2@bannerhealth.com",
    description="A Python package for PET Only image processing",
)
