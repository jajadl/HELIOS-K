import subprocess
import bz2
import os
import shutil

folder = 'https://hitran.org/files/HITEMP/bzip2format/'
CH4_file = "06_HITEMP2020.par.bz2"

def main():

    # Download HITEMP data
    cmd = 'wget --load-cookies=cookies.txt '+folder+CH4_file
    subprocess.run(cmd.split())
    os.rename(CH4_file, 'downloads/'+CH4_file)

    # unzip the HITEMP data
    with open('extract/'+CH4_file[:-4], 'wb') as new_file, bz2.BZ2File('downloads/'+CH4_file, 'rb') as f:
        for data in iter(lambda : f.read(100 * 1024), b''):
            new_file.write(data)

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITEMP2020" in a:
                aa = a.replace("HITEMP2020",'hitemp20')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 06 -ISO 1 -in hitemp20"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp20" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp20.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
