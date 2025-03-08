import sys
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

def get_mni_atlas_path():
    with ir.path("spmpup.data", "AAL3v1.nii") as p:
        return Path(p)
    
def get_mni_labels_path():
    with ir.path("spmpup.data", "AAL3v1.txt") as p:
        return Path(p)