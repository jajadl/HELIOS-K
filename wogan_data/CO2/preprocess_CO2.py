import subprocess
import bz2
import os
import shutil
from tqdm import tqdm

folder = 'https://hitran.org/files/HITEMP/bzip2format/'
CO2_file = '02_HITEMP2024.par.bz2'

def decompress_bz2_with_progress(input_path, output_path):
    """Decompresses a bz2 file and displays a progress bar.

    Args:
        input_path (str): Path to the input bz2 file.
        output_path (str): Path to save the decompressed output.
    """
    total_size = os.path.getsize(input_path)

    with bz2.open(input_path, 'rb') as bz2_file, open(output_path, 'wb') as output_file:
        with tqdm(desc=input_path, total=total_size, unit='iB', unit_scale=True, unit_divisor=1024) as pbar:
            while True:
                chunk = bz2_file.read(1024)
                if not chunk:
                    break
                output_file.write(chunk)
                pbar.update(len(chunk))

def main():

    # Download HITEMP data
    cmd = 'wget --load-cookies=cookies.txt '+folder+CO2_file
    subprocess.run(cmd.split())
    os.rename(CO2_file, 'downloads/'+CO2_file)

    # unzip the HITEMP data
    decompress_bz2_with_progress('downloads/'+CO2_file, 'extract/'+CO2_file[:-4])

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITEMP2024" in a:
                aa = a.replace("HITEMP2024",'hitemp24')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 02 -ISO 1 -in hitemp24"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp24" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp24.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
