import subprocess
from wogan_data import bins

# For running heliosk multiple times for different T values

def run(param_file):

    # loop over temperature bins
    for T in bins.T_grid:

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