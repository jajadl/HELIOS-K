import subprocess
import os
import shutil
import zipfile
import hapi

def get_global_ids(molecule):
    global_ids = []
    for key in hapi.ISO:
        if molecule == hapi.ISO[key][-1]:
            global_ids.append(hapi.ISO[key][0])
    return global_ids

def get_molecule_id(molecule):
    val = None
    for key in hapi.ISO:
        if molecule == hapi.ISO[key][-1]:
            val = key[0]
            break
    return val

def download_isotope_files(molecule):
    global_ids = get_global_ids(molecule)
    for val in global_ids:
        # isotope stuff
        url = 'https://hitran.org/data/Q/q'
        cmd = f'curl -o data/q{val}.txt {url}{val}.txt'  # Use -o to specify output path
        subprocess.call(cmd.split())
    return global_ids

def main():

    molecule = 'C2H6'
    global_ids = download_isotope_files(molecule)
    molecule_id = get_molecule_id(molecule)

    # Download
    hapi.fetch_by_ids(molecule, global_ids, 0, 1000000.0)
    os.remove(molecule+'.header')

    # Move to extract
    os.rename(molecule+'.data', 'extract/'+str(molecule_id)+'_HITRAN2016.par')

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITRAN2016" in a:
                aa = a.replace("HITRAN2016",'hitran16')

            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M "+str(molecule_id)+" -in hitran16"
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
