import argparse
import nibabel as nib
import pandas as pd
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="""
        Extract mean values from a PET image using an ROI atlas.
        For each label in the atlas, compute the number of non-zero voxels 
        (in the PET image) and the mean intensity of those non-zero voxels.
    """)
    parser.add_argument('--atlas', required=True, help='Path to the atlas NIfTI file.')
    parser.add_argument('--pet', required=True, help='Path to the PET NIfTI file.')
    parser.add_argument('--labels', required=True, help='Path to the text file with label indices and names.')
    parser.add_argument('--suv', required=True, help='Output CSV filename.')
    args = parser.parse_args()
    extract_suv(args.atlas, args.pet, args.labels, args.suv)
    return None

def extract_suv(atlas, pet, labels, suv):
    
    # Load the atlas and PET data
    atlas_nifti = nib.load(atlas)
    pet_nifti = nib.load(pet)
    
    atlas_data = atlas_nifti.get_fdata().astype(int)
    pet_data = pet_nifti.get_fdata()
    print(type(labels))
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
    df.to_csv(suv, index=False)
    return suv

if __name__ == '__main__':
    main()
