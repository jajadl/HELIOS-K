import subprocess
import bz2
import os
import shutil

folder = 'https://hitran.org/files/HITEMP/bzip2format/'
ffile = "04_HITEMP2019.par.bz2"

def main():

    cmd = 'wget https://hitran.org/data/Q/q21.txt'
    subprocess.run(cmd.split())
    os.rename('q21.txt', 'data/q21.txt')

    # Download HITEMP data
    cmd = 'wget --load-cookies=../../cookies.txt '+folder+ffile
    subprocess.run(cmd.split())
    os.rename(ffile, 'downloads/'+ffile)

    # unzip the HITEMP data
    with open('extract/'+ffile[:-4], 'wb') as new_file, bz2.BZ2File('downloads/'+ffile, 'rb') as f:
        for data in iter(lambda : f.read(100 * 1024), b''):
            new_file.write(data)

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITEMP2019" in a:
                aa = a.replace("HITEMP2019",'hitemp19')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 04 -ISO 1 -in hitemp19"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp19" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp19.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
