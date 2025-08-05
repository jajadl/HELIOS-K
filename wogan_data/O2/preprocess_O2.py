import subprocess
import os
import shutil

def download_partition_functions():
    """Download partition function files for O2 isotopologues"""
    os.makedirs('data', exist_ok=True)
    
    # O2 isotopologues use q36.txt, q37.txt, q38.txt
    q_files = [36, 37, 38]
    
    # Check if wget or curl is available
    import platform
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
    os.makedirs('extract', exist_ok=True)
    
    # Copy the .par file directly (no unzipping needed)
    shutil.copy('downloads/07_HITRAN2016.par', 'extract/07_HITRAN2016.par')
    
    # copy files to the main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            if "HITRAN2016" in a:
                aa = a.replace("HITRAN2016",'hitran16')
            shutil.copy('extract/'+a, '../../'+aa)
            tmp_files.append(aa)
    
    # preprocess the files (NO -ISO flag = all isotopologues)
    cmd = "./hitran -M 07 -in hitran16"
    subprocess.run(cmd.split(), cwd='../../')
    
    # move processed data files into data dir
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