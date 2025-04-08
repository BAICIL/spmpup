import argparse
import nibabel as nib
import pandas as pd
import numpy as np
import os

def main():
    """
    Extract mean values from a PET image using an ROI atlas.
    
    For each label in the atlas, compute the number of non-zero voxels 
    (in the PET image) and the mean intensity of those non-zero voxels.
    
    Parameters
    ----------
    atlas : str
        Path to the atlas NIfTI file.
    pet : str
        Path to the PET NIfTI file.
    labels : str
        Path to the text file with label indices and names.
    suvr : str
        Output CSV filename.
    fov : str, optional
        Path to the FOV file. Default is None.
            
    """
    parser = argparse.ArgumentParser(description="""
        Extract mean values from a PET image using an ROI atlas.
        For each label in the atlas, compute the number of non-zero voxels 
        (in the PET image) and the mean intensity of those non-zero voxels.
    """)
    parser.add_argument('--atlas', required=True, help='Path to the atlas NIfTI file.')
    parser.add_argument('--pet', required=True, help='Path to the PET NIfTI file.')
    parser.add_argument('--labels', required=True, help='Path to the text file with label indices and names.')
    parser.add_argument('--suvr', required=True, help='Output CSV filename.')
    parser.add_argument('--fov', required=False, default=None, help='Path to the FOV file.')
    args = parser.parse_args()
    _ = extract_suv(args.atlas, args.pet, args.labels, args.suvr, args.fov)
    return None

def extract_suv(atlas, pet, labels, suvr, fov=None):
    
    # Load the atlas and PET data
    """
    Extract mean values from a PET image using an ROI atlas.

    Parameters
    ----------
    atlas : str
        Path to the atlas NIfTI file.
    pet : str
        Path to the PET NIfTI file.
    labels : str
        Path to the text file with label indices and names.
    suvr : str
        Output CSV filename.
    fov : str, optional
        Path to the FOV file. Default is None.

    Returns
    -------
    suvr : str
        Path to the output CSV file.

    Notes
    -----
    For each label in the atlas, compute the number of non-zero voxels
    (in the PET image) and the mean intensity of those non-zero voxels.
    """
    if not os.path.isfile(atlas):
        raise FileNotFoundError(f"File not found: {atlas}")
    if not os.path.isfile(pet):
        raise FileNotFoundError(f"File not found: {pet}")
    
    try:
        atlas_nifti = nib.load(atlas)
        atlas_data = atlas_nifti.get_fdata().astype(int)
    except Exception as e:
        raise Exception(f"Failed to load ATLAS file: {e}")
    
    if fov is not None:
        if not os.path.isfile(fov):
            raise FileNotFoundError(f"PETFOV file not found: {fov}")
        
        try:
            fov_img = nib.load(fov)
            fov_data = fov_img.get_fdata()
        except Exception as e:
            raise Exception(f"Error loading PETFOV image: {e}")

        # Validate dimensions between the PETFOV image and the reference mask.
        if fov_data.shape != atlas_data.shape:
            raise ValueError(f"Dimension mismatch: PETFOV image shape {fov_data.shape} and "
                             f"reference mask shape {atlas_data.shape}")
        
        # Multiply the reference mask with the PETFOV data.
        atlas_data = atlas_data * fov_data
    
    try:
        pet_nifti = nib.load(pet)
        pet_data = pet_nifti.get_fdata()
    except Exception as e:
        raise Exception(f"Failed to load PET file: {e}")
    
    if atlas_data.shape != pet_data.shape:
        raise ValueError("Atlas and PET images must have the same shape.")
    
    # Read the label information
    # Expecting each line: "label_index ROI_name"
    labels_list = []
    with open(labels, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            label_index = int(parts[0])
            roi_name = " ".join(parts[1:])  # handle label names with spaces
            labels_list.append((label_index, roi_name))
    
    results = []
    
    for label_index, roi_name in labels_list:
        # Mask for the region in the atlas
        roi_mask = (atlas_data == label_index)
        
        # Extract PET values in that region
        pet_roi_vals = pet_data[roi_mask]
        
        # Consider only non-zero PET values
        non_zero_vals = pet_roi_vals[pet_roi_vals != 0]
        
        # Compute the mean and voxel count
        if len(non_zero_vals) > 0:
            mean_val = np.mean(non_zero_vals)
            count_nonzero = len(non_zero_vals)
        else:
            mean_val = 0
            count_nonzero = 0
        
        results.append({
            'Label': label_index,
            'ROI_Name': roi_name,
            'NonZeroVoxelCount': count_nonzero,
            'MeanValue': mean_val
        })
    
    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['Label','ROI_Name','NonZeroVoxelCount','MeanValue'])
    
    # Save to CSV
    try:
        df.to_csv(suvr, index=False)
    except Exception as e:
        raise Exception(f"Failed to save CSV file: {e}")
    
    return suvr

if __name__ == '__main__':
    main()
