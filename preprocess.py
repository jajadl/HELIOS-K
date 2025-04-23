
import subprocess

def main():
    
    species = ['C2H2','C2H6','CH4','CO','CO2','H2O','HCl','N2O','NH3','O2','O3','OCS','SO2']
    for sp in species:
        print(sp)
        cmd = 'python preprocess_'+sp+'.py'
        res = subprocess.run(cmd.split(), cwd='wogan_data/'+sp)
        assert res.returncode == 0

if __name__ == '__main__':
    main()