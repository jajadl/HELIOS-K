import subprocess
from wogan_data.bins import T_grid
import os
import numpy as np
import preprocess

# For running heliosk multiple times for different T values

def run(species, param_file):

    found = False
    if 'Out_'+species+'_bin0000.dat' in os.listdir('.'):
        results = np.loadtxt('Out_'+species+'_bin0000.dat')
        found = True

    if found:
        T_max = np.max(results[:,2])
        ind = np.argmin(np.abs(T_grid-T_max))
        TT = T_grid[ind+1:]
    else:
        TT = T_grid

    # loop over temperature bins
    for T in TT:

        # copy parameters file
        with open(param_file,'r') as f:
            lines = f.readlines()
        lines[1] = "T = "+'%.10f'%T+'\n'
        with open('param.dat','w') as f:
            for line in lines:
                f.write(line)

        res = subprocess.run("./heliosk")
        assert res.returncode == 0

def run_all(): 
    preprocess.main()
    species = ['C2H2','C2H6','CH4','CO','CO2','H2O','HCl','N2O','NH3','O2','O3','OCS','SO2']
    for sp in species:
        param_file = "wogan_data/"+sp+"/param.dat_"+sp
        run(sp, param_file)

if __name__ == "__main__":
    # param_file = "wogan_data/H2O/param.dat_H2O"
    # run(param_file)
    run_all()