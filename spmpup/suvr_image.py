#!/usr/bin/env python

import os
import argparse
import logging
import nibabel as nib
import numpy as np
from importlib import resources

# Dictionary mapping reference region names to their corresponding mask filenames.
REF_REGIONS = {
    'cerebellum': 'cerebellum_mask.nii.gz',
    'pons': 'pons_mask.nii.gz',
    # Add additional reference regions as needed.
}

def compute_suvr(pet_image_path, ref_region, output_path):
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
    ref_region : str
        Name of the reference region. Must be one of the keys in REF_REGIONS.
    output_path : str
        Path where the computed SUVR image will be saved.

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
    logging.info("Starting SUVR computation.")

    # Check if PET image exists.
    if not os.path.isfile(pet_image_path):
        logging.error("PET image file not found: %s", pet_image_path)
        raise FileNotFoundError(f"PET image file not found: {pet_image_path}")

    # Validate the reference region.
    if ref_region not in REF_REGIONS:
        logging.error("Reference region '%s' is not recognized. Available regions: %s", 
                      ref_region, list(REF_REGIONS.keys()))
        raise ValueError(f"Reference region '{ref_region}' is not recognized. "
                         f"Available regions: {list(REF_REGIONS.keys())}")

    try:
        # Load the PET image.
        pet_img = nib.load(pet_image_path)
        pet_data = pet_img.get_fdata()
        logging.info("Loaded PET image with shape: %s", pet_data.shape)
    except Exception as e:
        logging.error("Error loading PET image: %s", e)
        raise Exception(f"Error loading PET image: {e}")

    # Retrieve the mask file using importlib.resources.
    mask_filename = REF_REGIONS[ref_region]
    try:
        # The 'data' package should be in your package structure with an __init__.py file.
        with resources.path("data", mask_filename) as mask_path_obj:
            mask_path = str(mask_path_obj)
        logging.info("Retrieved reference mask file from package resources: %s", mask_path)
    except Exception as e:
        logging.error("Error retrieving the reference mask file using importlib.resources: %s", e)
        raise Exception("Error retrieving the reference mask file: " + str(e))

    # Check if the mask file exists.
    if not os.path.isfile(mask_path):
        logging.error("Reference mask file not found: %s", mask_path)
        raise FileNotFoundError(f"Reference mask file not found: {mask_path}")

    try:
        # Load the reference mask image.
        mask_img = nib.load(mask_path)
        mask_data = mask_img.get_fdata()
        logging.info("Loaded mask image with shape: %s", mask_data.shape)
    except Exception as e:
        logging.error("Error loading reference mask image: %s", e)
        raise Exception(f"Error loading reference mask image: {e}")

    # Ensure that the dimensions of the PET image and the mask match.
    if pet_data.shape != mask_data.shape:
        logging.error("Dimension mismatch: PET image shape %s, mask image shape %s", 
                      pet_data.shape, mask_data.shape)
        raise ValueError(f"Dimension mismatch: PET image shape {pet_data.shape} and "
                         f"mask image shape {mask_data.shape}")

    # Get PET values within the reference mask.
    masked_values = pet_data[mask_data > 0]
    if masked_values.size == 0:
        logging.error("No voxels found in the reference mask.")
        raise ValueError("No voxels found in the reference mask.")

    # Compute the mean value from the masked PET data.
    mean_value = np.mean(masked_values)
    if mean_value == 0:
        logging.error("Mean value of the reference region is zero. Cannot compute SUVR.")
        raise ValueError("Mean value of the reference region is zero. Cannot compute SUVR.")
    logging.info("Computed mean value in reference region: %f", mean_value)

    # Compute the SUVR image by dividing the PET image by the mean reference value.
    suvr_data = pet_data / mean_value
    logging.info("Computed SUVR image.")

    # Create a new NIfTI image for the SUVR data.
    suvr_img = nib.Nifti1Image(suvr_data, pet_img.affine, pet_img.header)

    try:
        # Save the SUVR image.
        nib.save(suvr_img, output_path)
        logging.info("SUVR image saved to: %s", output_path)
    except Exception as e:
        logging.error("Error saving SUVR image: %s", e)
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
        "--ref_region", required=True,
        help=f"Reference region name. Must be one of: {list(REF_REGIONS.keys())}."
    )
    parser.add_argument(
        "--out", required=True,
        help="Path to save the computed SUVR image."
    )
    args = parser.parse_args()

    # Configure logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        compute_suvr(args.pet, args.ref_region, args.out)
    except Exception as e:
        logging.error("SUVR computation failed: %s", e)
        exit(1)

if __name__ == "__main__":
    main()
