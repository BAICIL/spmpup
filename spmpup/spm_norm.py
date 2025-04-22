import sys
from datetime import datetime
import argparse
from spmpup import utils
import nibabel as nib
import subprocess

def get_job_template():
    '''
    Creating a template batch file for spm's old normalization job. 

    Returns:
        JOB_TEMPLATE (str): Text of the template batch file
    '''
    JOB_TEMPLATE = r"""%-----------------------------------------------------------------------
    % Job saved on <DATETIME> by cfg_util (rev $Rev: 7345 $)
        % spm SPM - Unknown
    % cfg_basicio BasicIO - Unknown
    %-----------------------------------------------------------------------
    matlabbatch{1}.spm.tools.oldnorm.estwrite.subj.source = <SOURCE>;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.subj.wtsrc = '';
    matlabbatch{1}.spm.tools.oldnorm.estwrite.subj.resample = <OUTPUT>;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.template = <TEMPLATE>;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.weight = '';
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.smosrc = 8;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.smoref = 0;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.regtype = 'mni';
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.cutoff = 25;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.nits = 16;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.eoptions.reg = 1;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.preserve = 0;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.bb = [NaN NaN NaN
                                                            NaN NaN NaN];
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.vox = [2 2 2];
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.interp = 1;
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.wrap = [0 0 0];
    matlabbatch{1}.spm.tools.oldnorm.estwrite.roptions.prefix = 'norm_';
    """

    return JOB_TEMPLATE

def create_4d_volume_list(nifti_path, nframes, petfov=None):
    """
    Creates a MATLAB-like cell array in the format:
    {
     '/path/img.nii,1'
     '/path/img.nii,2'
    }

    Args:
        nifti_path (str): File path for the 4D nifti image
        nframes (int): Number of frames to be used for creating the cell array

    Returns:
        vol_list (str): MATLAB-like cell array
    """
    lines = ["{"] # start of the cell array
    for i in range(1, nframes + 1):
        lines.append(f"'{nifti_path},{i}'")
    if petfov is not None:
        lines.append(f"'{petfov},1'")
    lines.append("}") # end of the cell array

    vol_list = "\n".join(lines)

    return vol_list

def create_batch(fpath, tracer_type, petfov=None):
    img = nib.load(fpath)
    n_frames = img.header['dim'][4]
    source_str = create_4d_volume_list(fpath, 1)
    template_pth = utils.get_pet_resource(tracer_type)
    template_str = create_4d_volume_list(template_pth, 1)
    output_str = create_4d_volume_list(fpath, n_frames, petfov)
    job_template = get_job_template()
    time = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    replaced_template = job_template.replace("<SOURCE>", source_str)
    replaced_template = replaced_template.replace("<OUTPUT>", output_str)
    replaced_template = replaced_template.replace("<TEMPLATE>", template_str)
    replaced_template = replaced_template.replace("<DATETIME>", time)
    with open ("/tmp/batch.m", 'w') as f:
        f.write(replaced_template)
    
    return "/tmp/batch.m"

def spmnorm(pet_file, mcr_location, script_path, tracer_type, fov_file=None):
    SCRIPT_PATH = script_path
    MCR_PATH = mcr_location
    
    batch_file = create_batch(pet_file, tracer_type, fov_file)

    out = subprocess.run([SCRIPT_PATH, MCR_PATH, "batch", batch_file], check=True, capture_output=True, text=True)
    print("Normalization done.")
    return None


def main():
    parser = argparse.ArgumentParser(description="SPM based normalization")
    parser.add_argument("--source", type=str, required=True, help="Path to the source file")
    parser.add_argument("--mcr", type=str, required=True, help="Path to the Matlab Runtime location")
    parser.add_argument("--script_path", type=str, required=True, help="Path to the location of the run_spm12.sh script")
    parser.add_argument("--tracer_type", type=str, required=True, 
                        choices=["fbp", "pib", "nav", "ftp", "mk"],
                        help="Choose one tracer type  from [fbp, pib, nav, ftp, mk].")
    parser.add_argument("--fov", type=str, required=False, default=None, help="Path to the FOV file")
    args = parser.parse_args()
    
    spmnorm(args.source, args.mcr, args.script_path, args.tracer_type, args.fov)


    return None

if __name__ == "__main__":
    main()