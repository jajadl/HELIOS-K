import subprocess
from wogan_data.bins import T_grid
import os
import numpy as np

# For running heliosk multiple times for different T values

def run(param_file):

    found = False
    for a in os.listdir('.'):
        if '_bin0000.dat' in a:
            results = np.loadtxt(a)
            found = True
            break

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

        subprocess.run("./heliosk")

if __name__ == "__main__":
    param_file = "wogan_data/H2O/param.dat_H2O"
    run(param_file)