import subprocess
import zipfile
import os
import shutil
import platform

def download_partition_functions():
    """Download partition function files for CO2 isotopologues"""
    os.makedirs('data', exist_ok=True)
    
    # CO2 isotopologues use q7.txt through q15.txt, q121.txt, q120.txt, q122.txt
    q_files = [7, 8, 9, 10, 11, 12, 13, 14, 15, 121, 120, 122]
    
    # Check if wget or curl is available
    if platform.system() == "Darwin":  # macOS
        download_cmd = "curl -o"
    else:  # Linux and others
        download_cmd = "wget -O"
    
    for q_num in q_files:
        url = f'https://hitran.org/data/Q/q{q_num}.txt'
        output_file = f'data/q{q_num}.txt'
        
        # Skip if file already exists
        if os.path.exists(output_file):
            print(f"q{q_num}.txt already exists, skipping...")
            continue
            
        cmd = f'{download_cmd} {output_file} {url}'
        print(f"Downloading q{q_num}.txt using {download_cmd.split()[0]}...")
        result = subprocess.call(cmd.split())
        
        if result != 0:
            print(f"Warning: Failed to download q{q_num}.txt")

def main():
    # Download partition function files FIRST
    download_partition_functions()
    
    # Create directories
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('extract', exist_ok=True)
    
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

    # Download HITEMP data
    download_tool = "wget" if platform.system() != "Darwin" else "curl -O"
    
    for ffile in files:
        if os.path.exists(f'downloads/{ffile}'):
            print(f"{ffile} already exists, skipping download...")
            continue
            
        if platform.system() == "Darwin":  # macOS
            cmd = f'curl -o downloads/{ffile} {folder}{ffile}'
        else:  # Linux
            cmd = f'wget --load-cookies=../../cookies.txt -O downloads/{ffile} {folder}{ffile}'
        
        print(f"Downloading {ffile}...")
        subprocess.run(cmd.split())

    # unzip the HITEMP data
    for ffile in files:
        print(f"Extracting {ffile}...")
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

    # preprocess the files (REMOVED -ISO 1 to get all isotopologues)
    cmd = "./hitran -M 02 -in hitemp10"
    subprocess.run(cmd.split(), cwd='../../')

    # move processed data files into data dir
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