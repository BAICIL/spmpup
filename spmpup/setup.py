from setuptools import setup, find_packages
# Full setup configuration
setup(
    name='spmpup',  
    version='0.1',  
    license='MIT License',
    description='A tool to process PET only images.',  
    author='Dhruman Goradia, PhD', 
    author_email='Dhruman.Goradia2@bannerhealth.com',  
    url='https://github.com/BAICIL/pypetup',
    
    # Automatically find and include all packages in the project
    packages=find_packages(),  
    include_package_data=True,
    package_data={
        "spmpup" = ["data/*.nii", "data/*.txt"],
    },

    # List dependencies (install_requires can also directly list dependencies if requirements.txt is not used)
    install_requires=[
        'numpy',
        'nibabel',
        'pandas'
    ],

    # Entry point configuration
    entry_points={
        'console_scripts': [
            'run_spmpup=spmpup.spm_petproc:main',  # Links the CLI script 'convert-to-nifti' to the 'main' function in cli.py
        ],
    },

    # Additional metadata
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOSX',
        'Operating System :: Linux'
    ],
    
    python_requires='>=3.9',  # Specifies that Python 3.9 or newer is required
)
