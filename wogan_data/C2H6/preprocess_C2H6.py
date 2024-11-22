import subprocess
import os
import shutil
import zipfile
import hapi

def main():

    # isotope stuff
    cmd = 'wget https://hitran.org/data/Q/q78.txt'
    subprocess.run(cmd.split())
    os.rename('q78.txt', 'data/q78.txt')

    # Download
    hapi.fetch('C2H6', 27, 1, 0, 1000000.0)
    os.remove('C2H6.header')

    # Move to extract
    os.rename('C2H6.data', 'extract/27_HITRAN2016.par')

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITRAN2016" in a:
                aa = a.replace("HITRAN2016",'hitran16')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 27 -ISO 1 -in hitran16"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitran16" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitran16.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
