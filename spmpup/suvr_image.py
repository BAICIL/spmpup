#!/usr/bin/env python

import os
import argparse
import nibabel as nib
import numpy as np
from importlib import resources

def compute_suvr(pet_image_path, ref_region_path, output_path, petfov_path=None):
    """
    Compute the SUVR image from a PET image using a reference region mask.

    The function loads a PET image in NIfTI format and a reference mask image from
    the package's data folder (using importlib.resources). It computes the mean value 
    within the masked region of the PET image and divides the entire PET image by this 
    mean value to generate the SUVR image. The result is then saved as a NIfTI file.

    Parameters
    ----------
    pet_image_path : str
        Path to the PET image file in NIfTI format.
    ref_region_path : str
        Path of the reference region file in NIfTI format.
    output_path : str
        Path where the computed SUVR image will be saved.
    petfov_path : str, optional
        Path to the PET field of view (FOV) file. Default is None.

    Raises
    ------
    FileNotFoundError
        If the PET image or reference mask file does not exist.
    ValueError
        If the reference region is not recognized, the PET and mask dimensions do not match,
        or if the mean value of the reference region is zero.
    Exception
        For other errors encountered during image processing.
    """
    print("Starting SUVR computation.")

    # Check if PET image exists.
    if not os.path.isfile(pet_image_path):
        raise FileNotFoundError(f"PET image file not found: {pet_image_path}")

    # Check if reference region exists.
    if not os.path.isfile(ref_region_path):
        raise FileNotFoundError(f"Reference region file not found: {ref_region_path}")
        
    try:
        # Load the PET image.
        pet_img = nib.load(pet_image_path)
        pet_data = pet_img.get_fdata()
        print(f"Loaded PET image with shape: {pet_data.shape}")
    except Exception as e:
        raise Exception(f"Error loading PET image: {e}")

    try:
        # Load the reference mask image.
        ref_mask_img = nib.load(ref_region_path)
        ref_mask_data = ref_mask_img.get_fdata()
        print(f"Loaded mask image with shape: {ref_mask_data.shape}")
    except Exception as e:
        raise Exception(f"Error loading reference mask image: {e}")
    
    if petfov_path is not None:
        if not os.path.isfile(petfov_path):
            raise FileNotFoundError(f"PETFOV file not found: {petfov_path}")
        try:
            petfov_img = nib.load(petfov_path)
            petfov_data = petfov_img.get_fdata()
        except Exception as e:
            raise Exception(f"Error loading PETFOV image: {e}")

        # Validate dimensions between the PETFOV image and the reference mask.
        if petfov_data.shape != ref_mask_data.shape:
            raise ValueError(f"Dimension mismatch: PETFOV image shape {petfov_data.shape} and "
                             f"reference mask shape {ref_mask_data.shape}")
        
        # Multiply the reference mask with the PETFOV data.
        ref_mask_data = ref_mask_data * petfov_data

    # Ensure that the dimensions of the PET image and the mask match.
    if pet_data.shape != ref_mask_data.shape:
        raise ValueError(f"Dimension mismatch: PET image shape {pet_data.shape} and "
                         f"mask image shape {ref_mask_data.shape}")

    # Get PET values within the reference mask.
    masked_values = pet_data[ref_mask_data > 0]
    if masked_values.size == 0:
        raise ValueError("No voxels found in the reference mask.")

    # Compute the mean value from the masked PET data.
    mean_value = np.mean(masked_values)
    if mean_value == 0:
        raise ValueError("Mean value of the reference region is zero. Cannot compute SUVR.")

    # Compute the SUVR image by dividing the PET image by the mean reference value.
    print("Computing SUVR image...")
    suvr_data = pet_data / mean_value

    # Create a new NIfTI image for the SUVR data.
    suvr_img = nib.Nifti1Image(suvr_data, pet_img.affine, pet_img.header)

    try:
        # Save the SUVR image.
        nib.save(suvr_img, output_path)
    except Exception as e:
        raise Exception(f"Error saving SUVR image: {e}")

def main():
    """
    Parse command-line arguments and compute the SUVR image.

    Example usage:
        python compute_suvr.py --pet /path/to/pet_image.nii.gz --ref_region cerebellum --out /path/to/output_suvr.nii.gz
    """
    parser = argparse.ArgumentParser(
        description="Compute SUVR image from a PET image using a reference region mask."
    )
    parser.add_argument(
        "--pet", required=True,
        help="Path to the PET image file in NIfTI format."
    )
    parser.add_argument(
        "--ref", required=True,
        help="Path to the reference region file in NIfTI format."
    )
    parser.add_argument(
        "--out", required=True,
        help="Path to save the computed SUVR image."
    )
    parser.add_argument(
        "--petfov", required=False, default=None,
        help="Path to the PETFOV image file in NIfTI format."
    )
    args = parser.parse_args()

    try:
        compute_suvr(args.pet, args.ref, args.out, args.petfov)
    except Exception as e:
        raise Exception(f"SUVR computation failed: {e}")

if __name__ == "__main__":
    main()
