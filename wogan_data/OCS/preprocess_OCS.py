import subprocess
import os
import shutil
import hapi
import requests

def main():

    # Download lines
    hapi.fetch('OCS', 19, 1, 1, 1_000_000)
    os.remove('OCS.header')
    tmpfile = '19_hitran.par'
    os.rename('OCS.data','../../'+tmpfile)

    # Download isotope file
    r = requests.get('https://hitran.org/data/Q/q59.txt')
    with open('data/q59.txt', "w") as f:
        f.write(r.text)

    # Process
    cmd = "./hitran -M 19 -ISO 1 -in hitran"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitran" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitran.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete tempfile
    os.remove('../../'+tmpfile)

if __name__ == "__main__":
    main()
