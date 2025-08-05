import subprocess
import zipfile
import os
import shutil
import platform

def download_partition_functions():
    """Download partition function files for H2O isotopologues"""
    os.makedirs('data', exist_ok=True)
    
    # H2O isotopologues use q1.txt through q6.txt, q129.txt
    q_files = [1, 2, 3, 4, 5, 6, 129]
    
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
    
    # Extract HITEMP 2010 files
    print("Extracting HITEMP 2010 files...")
    hitemp_files = []
    if os.path.exists('downloads/HITEMP_2010'):
        for fname in os.listdir('downloads/HITEMP_2010'):
            if fname.endswith('.zip') and '01_' in fname:
                hitemp_files.append(fname)
                print(f"Extracting {fname}...")
                with zipfile.ZipFile(f'downloads/HITEMP_2010/{fname}', 'r') as zip_ref:
                    zip_ref.extractall('extract')
    
    # Extract HITRAN 2016 file
    print("Extracting HITRAN 2016 file...")
    if os.path.exists('downloads/01_HITRAN2016.par'):
        shutil.copy('downloads/01_HITRAN2016.par', 'extract/01_HITRAN2016.par')
    else:
        print("Warning: 01_HITRAN2016.par not found in downloads/")
    
    # Copy and rename files to main directory
    tmp_files = []
    for a in os.listdir('extract'):
        if '.par' in a:
            aa = None
            if "HITEMP2010" in a:
                aa = a.replace("HITEMP2010", 'hitemp10hitran16')
            elif "HITRAN2016" in a:
                aa = a.replace("HITRAN2016", 'hitemp10hitran16')
            
            if aa:
                # Fix filename formatting for HITEMP files
                if 'hitemp10hitran16' in aa and '_' in aa:
                    tmp = aa.split('_')
                    if len(tmp) >= 2 and '-' in tmp[1]:
                        start = tmp[1].split('-')[0]
                        end = tmp[1].split('-')[1]
                        # Pad with zeros
                        start = start.rjust(5, '0')
                        end = end.rjust(5, '0') 
                        tmp[1] = start + '-' + end
                        aa = "_".join(tmp)
                
                print(f"Copying {a} -> {aa}")
                shutil.copy('extract/'+a, '../../'+aa)
                tmp_files.append(aa)
    
    if not tmp_files:
        print("ERROR: No files were processed. Check your downloads/ structure.")
        return
    
    print(f"Processing {len(tmp_files)} combined files...")
    
    # Preprocess the combined files (all isotopologues)
    cmd = "./hitran -M 01 -in hitemp10hitran16"
    subprocess.run(cmd.split(), cwd='../../')
    
    # Move processed data files into data dir
    for a in os.listdir('../../'):
        if "hitemp10hitran16" in a and ".bin" in a:
            os.rename('../../'+a, "data/"+a)
        if "hitemp10hitran16" in a and ".param" in a:
            os.rename('../../'+a, "data/"+a)
    
    # Delete the temporary files (only if they still exist)
    for tmp in tmp_files:
        tmp_path = '../../'+tmp
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    
    print("H2O combined preprocessing complete!")

if __name__ == "__main__":
    main()