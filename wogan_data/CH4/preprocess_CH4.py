import subprocess
import bz2
import os
import shutil
import platform

def download_partition_functions():
    """Download partition function files for CH4 isotopologues"""
    os.makedirs('data', exist_ok=True)
    
    # CH4 HITEMP 2020 isotopologues use q61.txt, q62.txt, q63.txt, q64.txt
    q_files = [61, 62, 63, 64]
    
    # Check if wget or curl is available
    if platform.system() == "Darwin":  # macOS
        download_cmd = "curl -o"
    else:  # Linux and others
        download_cmd = "wget -O"
    
    for q_num in q_files:
        url = f'https://hitran.org/data/Q/q{q_num}.txt'
        output_file = f'data/q{q_num}.txt'
        
        if os.path.exists(output_file):
            continue
            
        cmd = f'{download_cmd} {output_file} {url}'
        subprocess.call(cmd.split())

def main():
    # Download partition function files
    download_partition_functions()
    
    # Create directories
    os.makedirs('extract', exist_ok=True)
    
    # Look for manually downloaded CH4 HITEMP file
    CH4_file = None
    for fname in os.listdir('downloads'):
        if fname.endswith('.bz2') and ('CH4' in fname or fname.startswith('06_')):
            CH4_file = fname
            break
    
    if not CH4_file:
        print("ERROR: No CH4 HITEMP .bz2 file found in downloads/")
        print("Please manually download CH4 HITEMP 2020 data and place in downloads/")
        return
    
    # Decompress the HITEMP data
    with open(f'extract/{CH4_file[:-4]}.par', 'wb') as new_file, bz2.BZ2File(f'downloads/{CH4_file}', 'rb') as f:
        for data in iter(lambda : f.read(100 * 1024), b''):
            new_file.write(data)

    # Copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITEMP2020" in a:
                aa = a.replace("HITEMP2020",'hitemp20')
                shutil.copy('extract/'+a, '../../'+aa)
                tmp_files.append(aa)

    # Preprocess the files (all isotopologues)
    cmd = "./hitran -M 06 -in hitemp20"
    subprocess.run(cmd.split(), cwd='../../')

    # Move processed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp20" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp20.param" in a:
            os.rename('../../'+a, "data/"+a)

    # Delete the temporary files
    for tmp in tmp_files:
        os.remove('../../'+tmp)

if __name__ == "__main__":
    main()