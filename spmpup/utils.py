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

def get_mni_template_path():
    with ir.path("spmpup.data", "NAV_MNI_Template.nii") as p:
        return Path(p)

def get_mni_atlas_path(atlas=None):
    atlas_dict = {
        'AAL': 'AAL3v1.nii'
    }
    if atlas is None:
        atlas = 'AAL'
    fname = atlas_dict[atlas]
    with ir.path("spmpup.data", fname) as p:
        return Path(p)

def get_mni_reference_path(roi=None):
    roi_dict = {
        'Cerebellum': 'Cerebellum.nii',
        'InfCerebellum': 'InfCerebellum.nii',
    }
    if roi is None:
        atlas = 'Cerebellum'
    fname = roi_dict[roi]
    with ir.path("spmpup.data", fname) as p:
        return Path(p)
        
def get_mni_labels_path():
    with ir.path("spmpup.data", "AAL3v1.txt") as p:
        return Path(p)
    
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
    
    