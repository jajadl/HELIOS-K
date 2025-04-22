import subprocess
import zipfile
import os
import shutil

folder = 'https://hitran.org/files/HITEMP/HITEMP-2010/CO2_line_list/'
files = """
02_00000-00500_HITEMP2010.zip
02_00500-00625_HITEMP2010.zip
02_00625-00750_HITEMP2010.zip
02_00750-01000_HITEMP2010.zip
02_01000-01500_HITEMP2010.zip
02_01500-02000_HITEMP2010.zip
02_02000-02125_HITEMP2010.zip
02_02125-02250_HITEMP2010.zip
02_02250-02500_HITEMP2010.zip
02_02500-03000_HITEMP2010.zip
02_03000-03250_HITEMP2010.zip
02_03250-03500_HITEMP2010.zip
02_03500-03750_HITEMP2010.zip
02_03750-04000_HITEMP2010.zip
02_04000-04500_HITEMP2010.zip
02_04500-05000_HITEMP2010.zip
02_05000-05500_HITEMP2010.zip
02_05500-06000_HITEMP2010.zip
02_06000-06500_HITEMP2010.zip
02_06500-12785_HITEMP2010.zip
""".split()

def main():

    # Download HITEMP data
    for ffile in files:
        cmd = 'wget --load-cookies=cookies.txt '+folder+ffile
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
                aa = a.replace("HITEMP2010",'hitemp10')

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
    cmd = "./hitran -M 02 -ISO 1 -in hitemp10"
    subprocess.run(cmd.split(), cwd='../../')

    # move processesed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp10" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp10.param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()
