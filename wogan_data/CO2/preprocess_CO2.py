import subprocess
import zipfile
import bz2
import os
import shutil

folder = 'https://hitran.org/files/HITEMP/bzip2format/'
CO2_file = '02_HITEMP2024.par.bz2'

def main():

    # Download HITEMP data
    cmd = 'wget --load-cookies=cookies.txt '+folder+CO2_file
    subprocess.run(cmd.split())
    os.rename(CO2_file, 'downloads/'+CO2_file)

    # unzip the HITEMP data
    with open('extract/'+CO2_file[:-4], 'wb') as new_file, bz2.BZ2File('downloads/'+CO2_file, 'rb') as f:
        for data in iter(lambda : f.read(100 * 1024), b''):
            new_file.write(data)

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
