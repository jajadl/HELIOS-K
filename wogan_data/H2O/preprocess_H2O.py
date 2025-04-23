import subprocess
import zipfile
import os
import shutil

folder = 'https://hitran.org/files/HITEMP/HITEMP-2010/H2O_line_list/'
files = """
01_00000-00050_HITEMP2010.zip
01_00050-00150_HITEMP2010.zip
01_00150-00250_HITEMP2010.zip
01_00250-00350_HITEMP2010.zip
01_00350-00500_HITEMP2010.zip
01_00500-00600_HITEMP2010.zip
01_00600-00700_HITEMP2010.zip
01_00700-00800_HITEMP2010.zip
01_00800-00900_HITEMP2010.zip
01_00900-01000_HITEMP2010.zip
01_01000-01150_HITEMP2010.zip
01_01150-01300_HITEMP2010.zip
01_01300-01500_HITEMP2010.zip
01_01500-01750_HITEMP2010.zip
01_01750-02000_HITEMP2010.zip
01_02000-02250_HITEMP2010.zip
01_02250-02500_HITEMP2010.zip
01_02500-02750_HITEMP2010.zip
01_02750-03000_HITEMP2010.zip
01_03000-03250_HITEMP2010.zip
01_03250-03500_HITEMP2010.zip
01_03500-04150_HITEMP2010.zip
01_04150-04500_HITEMP2010.zip
01_04500-05000_HITEMP2010.zip
01_05000-05500_HITEMP2010.zip
01_05500-06000_HITEMP2010.zip
01_06000-06500_HITEMP2010.zip
01_06500-07000_HITEMP2010.zip
01_07000-07500_HITEMP2010.zip
01_07500-08000_HITEMP2010.zip
01_08000-08500_HITEMP2010.zip
01_08500-09000_HITEMP2010.zip
01_09000-11000_HITEMP2010.zip
01_11000-30000_HITEMP2010.zip
""".split()

def main():

    # Download HITEMP data
    for ffile in files:
        cmd = 'wget --load-cookies=../../cookies.txt '+folder+ffile
        subprocess.run(cmd.split())
        os.rename(ffile, 'downloads/'+ffile)

    # unzip the HITEMP data
    for ffile in files:
        with zipfile.ZipFile('downloads/'+ffile, 'r') as zip_ref:
            zip_ref.extractall('extract')

    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if 'par' in a:
            if "HITEMP2010" in a:
                aa = a.replace("HITEMP2010",'hitemp10hitran16')
            if "HITRAN2016" in a:
                aa = a.replace("HITRAN2016",'hitemp10hitran16')

            tmp = aa.split('_')
            start = tmp[1].split('-')[0]
            start = start.rjust(5, '0')
            end = tmp[1].split('-')[1]
            end = end.rjust(5, '0')
            tmp[1] = start+'-'+end
            aa = "_".join(tmp)
            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)

    # preprocess the files
    cmd = "./hitran -M 01 -ISO 1 -in hitemp10hitran16"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp10hitran16" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp10hitran16.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
