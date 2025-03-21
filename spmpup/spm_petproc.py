import argparse
import os

import pypetup as pup
import spmpup
import spmpup.spm_norm
import spmpup.suv
import spmpup.utils


def run_pup(
    pet_nifti,
    pet_json=None,
    derivatives_dir=None,
    start_time=None,
    duration=None,
    mcr_path,
    spm_path
):

    print("Copying PET data to derivatives directory")
    input_pet_dir = os.path.dirname(pet_nifti)
    input_pet_filename = os.path.basename(pet_nifti)
    input_pet_filename_without_extension = input_pet_filename.split(".")[0]

    if pet_json is None:
        pet_json = os.path.join(
            input_pet_dir, input_pet_filename_without_extension + ".json"
        )

    if derivatives_dir is None:
        process_folder = os.path.join(input_pet_dir, "derivatives")
        os.makedirs(process_folder, exist_ok=True)
    else:
        parts = input_pet_filename.split("_")
        subject_id = parts[0]
        session_id = parts[1]
        tracer = parts[2][7:]
        process_folder = os.path.join(derivatives_dir, subject_id, session_id, tracer)
        os.makedirs(process_folder, exist_ok=True)

    copy_pet_nifti = os.path.join(process_folder, input_pet_filename)
    copy_pet_json = os.path.join(
        process_folder, input_pet_filename_without_extension + ".json"
    )

    _ = pup.time_function(pup.copy_file, **{"src": pet_json, "dest": copy_pet_json})
    _ = pup.time_function(pup.copy_file, **{"src": pet_nifti, "dest": copy_pet_nifti})

    print("Performing motion correction")
    mocofile = pup.time_function(pup.perform_motion_correction, (copy_pet_nifti))

    print("Get model frame indices")
    start_frame, end_frame = pup.find_frame_indices(copy_pet_json, start_time, duration)

    print("Generate msum image")
    data = pup.load_json(copy_pet_json)
    half_life = data["RadionuclideHalfLife"]
    start_times = data["FrameTimesStart"]
    durations = data["FrameDuration"]
    decay_factors = data["DecayFactor"]
    msumfile = pup.time_function(
        pup.model_sum_pet,
        *(
            mocofile,
            start_frame,
            end_frame,
            half_life,
            start_times,
            durations,
            decay_factors,
        )
    )

    unzip_msum = spmpup.utils.gunzip_file(msumfile)
    unzip_msum_norm_dir = os.path.dirname(unzip_msum)
    unzip_msum_norm_fn = os.path.basename(unzip_msum)
    unzip_msum_norm = os.path.join(unzip_msum_norm_dir, f"norm_{unzip_msum_norm_fn}") 
    spmpup.spm_norm.spmnorm(unzip_msum, mcr_path, spm_path)

    print("Generate SUV table for AAL3v1")
    atlas = spmpup.utils.get_mni_atlas_path()
    labels = spmpup.utils.get_mni_labels_path()
    suv = os.path.join(unzip_msum_norm_dir, "AAL3v1_SUV.csv")
    suv_file = spmpup.suv.extract_suv(atlas, unzip_msum_norm, labels, suv)
    print(f"{suv_file} is generated.")
    

def main():
    """
    Main Function to handle command-line arguments and perform PET processing.

    Uses argparse to campture command-line inputs.
    """
    parser = argparse.ArgumentParser(
        description="Process PET data using the PUP workflow."
    )
    parser.add_argument(
        "--pet_nifti", type=str, required=True, help="Path to the input PET file."
    )
    parser.add_argument(
        "--pet_json",
        type=str,
        required=False,
        default=None,
        help="Path to the input PET JSON file.",
    )
    parser.add_argument(
        "--derivatives_dir",
        type=str,
        required=False,
        default=None,
        help="Path to the base directory (optonal, default=None).",
    )
    parser.add_argument(
        "--start_time",
        type=float,
        required=False,
        default=None,
        help="Start time for frames of interest (optional, default=None)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=False,
        default=None,
        help="Total duration for frames of interest (optional, default=None)",
    )
    parser.add_argument(
        "--mcr_path",
        type=str,
        required=True,
        help="Path to Matlab Runtime"
    )
    parser.add_argument(
        "--spm_path",
        required=True,
        type=str,
        help="Path to the run_spm12.sh script"
    )
    args = parser.parse_args()

    result = pup.time_function(
        run_pup,
        *(
            args.pet_nifti,
            args.pet_json,
            args.derivatives_dir,
            args.start_time,
            args.duration,
            args.mcr_path,
            args.spm_path
        )
    )


if __name__ == "__main__":
    main()
