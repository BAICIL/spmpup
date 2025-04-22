import sys
import nibabel as nib
import numpy as np
from datetime import datetime
import os
import subprocess
from pathlib import Path
import importlib.resources as ir

def is_gzipped(file_path):
    """
    Checks if the file at file_path is gzipped by reading its first two bytes (gzip magic number).

    Args:
        file_path (str): path of the input file

    Returns:
        (boolean): True if the file is gzipped, False otherwise
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'rb') as f:
        magic = f.read(2)
    return magic == b'\x1f\x8b'

def gunzip_file(file_path):
    """
    Decompresses file_path if it is gzipped, overwriting
    the original file.
    """
    if not is_gzipped(file_path):
        print(f"{file_path} is not gzipped. No action taken.")
        return file_path
    
    out = subprocess.run(["gunzip", file_path], capture_output=True, check=True, text=True)

    return file_path.rstrip('.gz')

def gzip_file(file_path):
    """
    Compress file_path if it is not gzipped, overwriting athe original file. 
    """
    if is_gzipped(file_path):
        print(f"{file_path} is already zipped. No action taken.")
        return file_path
    
    out = subprocess.run(["gzip", "-9", file_path], capture_output=True, check=True, text=True)

    return file_path + '.gz'
        
def create_pet_fov(pet_file, crop_idx=2):
    """
    Create a PET field of view (FOV) file. Clip the Superior 2 and 
    Inferior 2 slices.

    Args:
    pet_file (str): Path to 3D PET image (eg. PET sum image)

    Returns:
    fov_file (str): Path to 3D PET FOV binary image.
    """
    try:
        pet_img = nib.load(pet_file)
        # checking if the image shape is 3d or 4d
        if len(pet_img.shape) not in [3, 4]:
            raise ValueError(
                f"Invalid image shape: {pet_img.shape}.\nOnly 3D or 4D images are supported."
            )
    except nib.filebasedimages.ImageFileError:
        raise ValueError(f"Error loading NIFTI file: {pet_file}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
    
    try:
        pet_data = pet_img.get_fdata()
        fov_mask = np.ones(pet_data.shape[:3], dtype=np.uint8)
        fov_mask[:, :, :crop_idx] = 0
        fov_mask[:, :, -crop_idx:] = 0
        fov_img = nib.Nifti1Image(fov_mask, pet_img.affine, pet_img.header)
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
    
    fov_dir = os.path.dirname(pet_file)
    fov_file = os.path.join(fov_dir, "petfov.nii.gz")
    try:
        nib.save(fov_img, fov_file)
    except IOError:
        raise IOError(f"Error saving NIFTI file: {fov_file}")
    
    return fov_file

TEMPLATES = {
    "fbp": "fbp_mni.nii",
    "pib": "pib_mni.nii",
    "nav": "nav_mni.nii",
    "mk": "mk_mni.nii",
    "ftp": "ftp_mni.nii"
}

ATLASES = {
    "aal": ("aal3v1.nii", "aal3v1.txt"),
    "avid2": ("avid_2labels.nii", "avid_2labels.txt"),
    "avid7": ("avid_7labels.nii", "avid_7labels.txt"),
    "npdka": ("npdka_aparc+aseg.nii", "npdka_aparc+aseg.txt")
}

REFERENCE = {
    "cerebellum": "avid_cerebellum.nii",
    "inf_cerebellum": "inferior_cerebellum.nii"
}

def get_pet_resource(resource = 'fbp'):
    """
    Retrieve the file path(s) for a PET template, reference region or atlas resource.

    Parameters:
        resource (str): Key for the resource, e.g., "fbp" for a template, "cerebellum" for a reference region or "aal" for an atlas.

    Returns:
        str: For a template, returns the file path as a string.
        str: For a reference region, returns the file path as a string.
        tuple: For an atlas, returns a tuple (image_path, label_path) as strings.

    Raises:
        ValueError: If the resource key is not found.
    
    """
    data_pkg = ir.files('spmpup.Data')
    
    if resource in TEMPLATES:
        filename = TEMPLATES[resource]
        return str(data_pkg.joinpath(filename))

    elif resource in ATLASES:
        image_filename, label_filename = ATLASES[resource]
        return str(data_pkg.joinpath(image_filename)), str(data_pkg.joinpath(label_filename))
    
    elif resource in REFERENCE:
        refname = REFERENCE[resource]
        return str(data_pkg.joinpath(refname))

    else:
        raise ValueError(f"Resource '{resource}' not found in templates or atlases.")
