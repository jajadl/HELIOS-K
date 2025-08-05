import subprocess
import bz2
import os
import shutil
import platform

def download_partition_functions():
    """Download partition function files for CO isotopologues"""
    os.makedirs('data', exist_ok=True)
    
    # CO isotopologues use q26.txt, q27.txt, q28.txt, q29.txt, q30.txt, q31.txt
    q_files = [26, 27, 28, 29, 30, 31]
    
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
    
    # Look for manually downloaded CO HITEMP file
    CO_file = None
    for fname in os.listdir('downloads'):
        if fname.endswith('.bz2') and ('CO' in fname or fname.startswith('05_')):
            CO_file = fname
            break
    
    if not CO_file:
        print("ERROR: No CO HITEMP .bz2 file found in downloads/")
        print("Please manually download CO HITEMP 2019 data and place in downloads/")
        return
    
    # Decompress the HITEMP data
    with open(f'extract/{CO_file[:-4]}.par', 'wb') as new_file, bz2.BZ2File(f'downloads/{CO_file}', 'rb') as f:
        for data in iter(lambda : f.read(100 * 1024), b''):
            new_file.write(data)

    # Copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITEMP2019" in a:
                aa = a.replace("HITEMP2019", 'hitemp19')
                # Ensure we don't have double .par extension
                if aa.endswith('.par.par'):
                    aa = aa[:-4]  # Remove the extra .par
                shutil.copy('extract/'+a, '../../'+aa)
                tmp_files.append(aa)

    # Preprocess the files (all isotopologues)
    cmd = "./hitran -M 05 -in hitemp19"
    subprocess.run(cmd.split(), cwd='../../')

    # Move processed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp19" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp19" in a and ".param" in a:
            os.rename('../../'+a, "data/"+a)

    # Delete the temporary files (only if they still exist)
    for tmp in tmp_files:
        tmp_path = '../../'+tmp
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    main()