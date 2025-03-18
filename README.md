### SPMPUP
SPM based PET only Unified Pipeline in Python.

This package perform quantative processing of PET only data in the absense of associated MRI T1 scan. The package performes the following steps:
* Motion Correction (using pypetup package)
* Sum Multiframe data (using pypetup package)
* Normalize the PET sum image to tracer specific MNI Template (using spmpup package) 
* Extract mean SUV values for ROIs defined by AAL atlas (ysing spmpup package)

# Pre-requisites 
* OS = MacOS or Linux
* Cat12 standalone version
* MATLAB Runtime 2023b
* FreeSurfer >= version 7 correctly configured
* FSL >= version 6 correctly configured
* pypetup package

# Install

1. Install CAT12 Standalone version which requires MATLAB runtime. The instructions for downloading and installing CAT12 standalone and MATLAB Runtime are available [here](https://neuro-jena.github.io/cat/index.html#DOWNLOAD)

2. Install pypetup package. The instructions are available [here](https://github.com/BAICIL/pypetup)

3. Clone the github repo:

```
pip install git+https://github.com/BAICIL/pypetup.git
```

# Usage
```
run_pup [-h] --pet_nifti PET_NIFTI 
            [--pet_json PET_JSON] 
            [--derivatives_dir DERIVATIVES_DIR] 
            --fs_dir FS_DIR 
            [--t1_filename T1_FILENAME] 
            [--start_time START_TIME] 
            [--duration DURATION] 
            [--norsf]

Process PET data using the PUP workflow.

options:
  -h, --help            
    show this help message and exit
  --pet_nifti PET_NIFTI 
    Path to the input PET file.
  --pet_json PET_JSON
    Path to the input PET JSON file.
  --derivatives_dir DERIVATIVES_DIR
    Path to the base directory (optional, default=None).
  --fs_dir FS_DIR
    Path of the Subjects FreeSurfer mri directory.
  --t1_filename T1_FILENAME
    File name with extension of the T1 file (optional, default=orig_nu.mgz) 
  --start_time START_TIME
    Start time for frames of interest (optional, default=None)
  --duration DURATION
    Total duration for frames of interest (optional, default=None)
  --norsf
    Do not perform RSF correction
```

# Example
1. Minimum inputs: In this case the derivatives directory will be created in the directory where the PET input data resides. The json file is assumed to be in the same location as the PET file with similar name as the nifti. All frames will be used as frames of interest. RSF PVC correction will be attempted.

```
run_pup --pet_nift /path/to/pet.nii.gz \
        --fs_dir /path/to/subject/mri 

```
2. Organized minimal inputs: In this case the derivatives directory will be provided by the user to better organize the output. In this case, the processed data will be located in the `derivatives/sub-XXX/ses-XXX/Tracer/`

```
run_pup --pet_nifti /path/to/pet.nii.gz \
        --derivatives_dir /path/to/derivatives
        --fs_dir /path/to/subject/mri
