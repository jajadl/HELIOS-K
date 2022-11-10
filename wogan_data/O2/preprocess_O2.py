import subprocess
import os
import shutil
def main():

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITRAN2016" in a:
                aa = a.replace("HITRAN2016",'hitran16')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 07 -ISO 1 -in hitran16"
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
