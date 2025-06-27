import numpy as np
import os
import sqlite3
import io
import h5py
import pandas as pd
from scipy import interpolate
import numba as nb
from wogan_data import bins as wogan_bins

T_GRID = wogan_bins.T_grid
P_GRID = wogan_bins.P_grid
WAVNUM = wogan_bins.wavnum

@nb.njit()
def reshape_data_array(data_array, nP, nT, nwno):
    k = np.empty((nT, nP, nwno),np.float32)
    for i1 in range(nT):
        for i2 in range(nP):
            for i3 in range(nwno):
                k[i1,i2,i3] = data_array[i3 + i2*nwno + i1*nP]
    return k

def get_wavenumbers():
    wavnums = WAVNUM[::-1]
    wno = np.array([])
    for i in range(len(wavnums)-1):
        wno = np.append(wno, np.linspace(wavnums[i],wavnums[i+1],100_001)[:-1])
    return wno

def make_db(heliosk_dir, data_dir, min_wavelength, max_wavelength, new_R, old_R=1e6):

    db = f'opacities_{min_wavelength}_{max_wavelength}_R{new_R}.db'

    if os.path.exists(db):
        os.remove(db)

    build_skeleton(db)

    # Get the filenames
    tmp = os.listdir(heliosk_dir)
    filenames = [a for a in tmp if 'Out_' in a and '.bin' in a]
    molecules = [a.replace('Out_','').replace('.bin','') for a in filenames]

    # Wavenumber grid
    wno = get_wavenumbers()

    # Insert line opacities
    for i,molecule in enumerate(molecules):
        print('Working on '+molecule)

        # Load the data
        data_array = np.fromfile(heliosk_dir+'/'+filenames[i], dtype=np.float32)

        # reshape the data
        k = reshape_data_array(data_array, len(P_GRID), len(T_GRID), len(wno))

        # Put molecule into database
        new_wvno_grid = insert_molecule(
            db, molecule, data_dir,
            min_wavelength, max_wavelength, new_R, 
            old_R, wno, T_GRID, P_GRID, k
        )

    # continuum
    print('Working on continuum')
    col_names = write_CIA_file(data_dir, 'continuum.txt')   
    restruct_continuum('continuum.txt', col_names, new_wvno_grid, db, overwrite=False)

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)

def open_local(db_f):
    """Code needed to open up local database, interpret arrays from bytes and return cursor"""
    conn = sqlite3.connect(db_f, detect_types=sqlite3.PARSE_DECLTYPES)
    #tell sqlite what to do with an array
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    cur = conn.cursor()
    return cur,conn

def create_grid(min_wavelength, max_wavelength, constant_R):
    """Simple function to create a wavelength grid defined with a constant R.

    Parameters
    ----------
    min_wavelength : float 
        Minimum wavelength in microns
    max_wavelength : float 
        Maximum wavelength in microns
    constant_R : float 
        Constant R spacing

    Returns
    -------
    wavenumber grid defined at constant Resolution
    """
    spacing = (2.*constant_R+1.)/(2.*constant_R-1.)
    
    npts = np.log(max_wavelength/min_wavelength)/np.log(spacing)
    
    wsize = int(np.ceil(npts))+1
    newwl = np.zeros(wsize)
    newwl[0] = min_wavelength
    
    for j in range(1,wsize):
        newwl[j] = newwl[j-1]*spacing
    
    return 1e4/newwl[::-1]

def build_skeleton(db_f):
    """
    This functionb builds a skeleton sqlite3 database with three tables:
        1) header
        2) molecular
        3) continuum

    Parameters
    ----------
    db_f : str
        str of database file name
    """
    cur, conn = open_local(db_f)
    #header
    command="""DROP TABLE IF EXISTS header;
    CREATE TABLE header (
        id INTEGER PRIMARY KEY,
        pressure_unit VARCHAR,
        temperature_unit VARCHAR,
        wavenumber_grid array,
        continuum_unit VARCHAR,
        molecular_unit VARCHAR
        );"""

    cur.executescript(command)
    #molecular data table, note the existence of PTID which will be very important
    command = """DROP TABLE IF EXISTS molecular;
    CREATE TABLE molecular (
        id INTEGER PRIMARY KEY,
        ptid INTEGER,
        molecule VARCHAR ,
        pressure FLOAT,
        temperature FLOAT,
        opacity array);"""

    cur.executescript(command)
    #continuum data table
    command = """DROP TABLE IF EXISTS continuum;
    CREATE TABLE continuum (
        id INTEGER PRIMARY KEY,
        molecule VARCHAR ,
        temperature FLOAT,
        opacity array);"""

    cur.executescript(command)
    
    conn.commit() #this commits the changes to the database
    conn.close()

def insert_molecule(
        new_db, molecule, data_dir,
        min_wavelength, max_wavelength, new_R, 
        old_R, og_wvno_grid, T, P, k,
        verbose=True
        ):
    """Insert molecule into PICASO opacity DB

    Parameters
    ----------
    new_db : str
        Filename of sqlite database.
    molecule : str
        Molecule name
    min_wavelength : float
        min wavelength in microns.
    max_wavelength : float
        max wavelength in microns.
    new_R : float
        Spectral resolution of the new database
    old_R : float
        Spectral resolution of the old database
    og_wvno_grid : float
        Wavenumber grid of LBL data.
    T : ndarray
        Array of temperatures in K
    P : ndarray
        Array of pressures in bar
    k : ndarray
        Opacities in cm^2/molecule. shape is `(len(T),len(P),len(og_wvno_grid))`.

    Returns
    -------
    new_wvno_grid: ndarray
        Wavenumber grid of the new resampling
    """    
    
    cur, conn = open_local(new_db)

    # Wavenumber grid that we will interpolate LBL opacities to
    interp_wvno_grid = create_grid(min_wavelength, max_wavelength, old_R)
    
    # Degree to which to downsample
    bins = int(old_R/new_R)

    # New wavenumber grid after downsampling
    new_wvno_grid = interp_wvno_grid[::bins]

    for i in range(len(T)):
        if verbose:
            print('Temperature = %i'%(T[i]))
        for j in range(len(P)):
            l = j + i*len(P)

            # Interpolate LBL opacity to a common grid
            dset = np.interp(interp_wvno_grid, og_wvno_grid, k[i,j,:], right=1e-50, left=1e-50)

            # Make smallest number 1e-200
            dset[dset<1e-200] = 1e-200 

            # Resample
            y = dset[::bins]

            # Add in photolysis cross sections
            filename = data_dir+'/xsections/'+molecule+'.h5'
            if os.path.exists(filename):
                with h5py.File(filename,'r') as f:
                    xs = f['photoabsorption'][:].astype(np.float64)[::-1]
                    wno = 1e4/(f['wavelengths'][:].astype(np.float64)[::-1]/1e3)
                y += np.interp(new_wvno_grid,wno,xs,left=1e-200,right=1e-200)

            cur.execute('INSERT INTO molecular (ptid, molecule, temperature, pressure,opacity) values (?,?,?,?,?)', (int(l),molecule,float(T[i]),float(P[j]), y))
                
    conn.commit()
    cur.execute('SELECT pressure_unit from header')
    p_find = cur.fetchall()
    if len(p_find) == 0:
        cur.execute('INSERT INTO header (pressure_unit, temperature_unit, wavenumber_grid, continuum_unit, molecular_unit) values (?,?,?,?,?)',
                ('bar','kelvin', np.array(new_wvno_grid), 'cm-1 amagat-2', 'cm2/molecule'))
        conn.commit()
    conn.close()

    return new_wvno_grid

def write_CIA_file(data_dir, filename):

    cia_dir = data_dir+'/CIA'
    tmp = os.listdir(cia_dir)
    filenames = [a for a in tmp if '.h5' in a]
    col_names = ['wno'] + [a.strip('.h5').replace('-','') for a in filenames]

    wvs = []
    Ts = []
    xss = []
    for file1 in filenames:
        with h5py.File(cia_dir + '/'+file1,'r') as f:
            
            # Zeros for high and lower wavelengths
            wv = f['wavelengths'][:]
            wv = np.concatenate((np.array([wv[0]*0.9999]),wv,np.array([wv[-1]*1.0001])))
            wvs.append(wv)
    
            # Extrapolate to higher and lower T
            T = f['T'][:]
            T = np.concatenate((np.array([0]),T,np.array([10000])))
            Ts.append(T)
    
            xs = f['log10xs'][:].T
            tmp = np.ones(xs.shape[0])*np.min(xs)
            tmp = tmp.reshape((len(tmp),1))
            xs = np.concatenate((tmp,xs,tmp),axis=1)
    
            tmp1 = xs[0,:].reshape((1,len(wv)))
            tmp2 = xs[-1,:].reshape((1,len(wv)))
            xs = np.concatenate((tmp1,xs,tmp2),axis=0)
            
            xss.append(xs)
    
    wv_grid = np.logspace(np.log10(0.1), np.log10(250), 1000)
    
    T_grid = np.arange(40, 3000.0+.1, 20)
    
    xs_grids = []
    for i in range(len(xss)):
        xs = xss[i]
        T = Ts[i]
        wv = wvs[i]
        f = interpolate.RegularGridInterpolator((T, wv), xs, bounds_error=False, fill_value=-153.82632446)
        Tg, wvg = np.meshgrid(T_grid, wv_grid, indexing='ij', sparse=True)
        xs_grid = f((Tg, wvg))
        xs_grids.append(xs_grid)
    
    Pstp = 1
    C = 1/1.013e6
    Tstp = 273.15
    k = 1.3807e-16
    Ca = (Pstp*(1/C))/(k*Tstp)
    
    fmt = '{:>14}'
    with open(filename,'w') as f:
        f.write('%i %i\n'%(len(wv_grid),len(T_grid)))
        for i in range(len(T_grid)):
            f.write('%.1f\n'%(T_grid[i]))
            for j in range(len(wv_grid)):
                k = len(wv_grid) - j - 1
                wno = 1e4/wv_grid[k]
                f.write(fmt.format('%.1f'%wno))
                for l in range(len(xs_grids)):
                    xs_grid = xs_grids[l]
                    xs = np.log10((10.0**xs_grid[i,k]) * Ca**2)
                    f.write(fmt.format('%.4f'%xs))
                f.write('\n')

    return col_names

def restruct_continuum(original_file,colnames, new_wno,new_db, overwrite):
    """
    The continuum factory takes the CIA opacity file and adds in extra sources of 
    opacity from other references to fill in empty bands. It assumes that the original file is 
    structured as following,with the first column wavenumber and the rest molecules: 
    1000 198
    75.
    0.0  -33.0000  -33.0000  -33.0000  -33.0000  -33.0000
    20.0   -7.4572   -7.4518   -6.8038   -6.0928   -5.9806
    40.0   -6.9547   -6.9765   -6.6322   -5.7934   -5.4823
    ... ... ... etc 

    Where 1000 corresponds to the number of wavelengths, 198 corresponds to the number of temperatures
    and 75 is the first temperature. If this structure changes, we will need to restructure this top 
    level __init__ function that reads it in the original opacity file. 
    
    Parameters
    ----------
    original_file : str
        Filepath that points to original opacity file (see description above)
    colnames : list 
        defines the sources of opacity in the original file. For the example file above, 
        colnames would be ['wno','H2H2','H2He','H2H','H2CH4','H2N2']
    new_wno : numpy.ndarray, list 
        wavenumber grid to interpolate onto (units of inverse cm)
    new_db : str 
        New database name 
    overwrite : bool 
        Default is set to False as to not overwrite any existing files. This parameter controls overwriting 
        cia database 
    """
    og_opacity, temperatures, old_wno, molecules = get_original_data(original_file,
        colnames, overwrite=overwrite,new_db=new_db)

    ntemp = len(temperatures)

    #restructure and insert to database 
    restructure_opacity(new_db,ntemp,temperatures,molecules,og_opacity,old_wno,new_wno)

def get_original_data(original_file,colnames,new_db, overwrite=False):
    """
    The continuum factory takes the CIA opacity file and adds in extra sources of 
    opacity from other references to fill in empty bands. It assumes that the original file is 
    structured as following,with the first column wavenumber and the rest molecules: 
    1000 198
    75.
    0.0  -33.0000  -33.0000  -33.0000  -33.0000  -33.0000
    20.0   -7.4572   -7.4518   -6.8038   -6.0928   -5.9806
    40.0   -6.9547   -6.9765   -6.6322   -5.7934   -5.4823
    ... ... ... etc 

    Where 1000 corresponds to the number of wavelengths, 198 corresponds to the number of temperatures
    and 75 is the first temperature. If this structure changes, we will need to restructure this top 
    level __init__ function that reads it in the original opacity file. 
    
    Parameters
    ----------
    original_file : str
        Filepath that points to original opacity file (see description above)
    colnames : list 
        defines the sources of opacity in the original file. For the example file above, 
        colnames would be ['wno','H2H2','H2He','H2H','H2CH4','H2N2']
    new_db : str 
        New database name 
    overwrite : bool 
        Default is set to False as to not overwrite any existing files. This parameter controls overwriting 
        cia database 
   """
    og_opacity = pd.read_csv(original_file,delim_whitespace=True,names=colnames)
    
    temperatures = og_opacity['wno'].loc[np.isnan(og_opacity[colnames[1]])].values

    og_opacity = og_opacity.dropna()
    old_wno = og_opacity['wno'].unique()
    #define units
    w_unit = 'cm-1'
    opacity_unit = 'cm-1 amagat^-2'
    molecules = colnames[1:]
    temperature_unit = 'K'
    
    #create database file
    if os.path.exists(new_db):
        if overwrite:
            raise Exception("Overwrite is set to false to save db's from being overwritten.")

    return og_opacity, temperatures, old_wno, molecules

def insert(cur,conn,mol,T,opacity):
    """Insert into """
    cur.execute('INSERT INTO continuum (molecule, temperature, opacity) values (?,?,?)', (mol,float(T), opacity))

def restructure_opacity(new_db,ntemp,temperatures,molecules,og_opacity,old_wno,new_wno):
    """
    Parameters
    ----------
    new_db : str 
        str of new database name
    ntemp : int
        int of number of temperatures
    temperatures : array
        array of temperatures
    molecules : list
        list of molecules to put in database
    og_opacity : pandas dataframe
        pandas dataframe of original opacity
    old_wno : array
        array of original wavenumbers
    new_wno : array
        array of new wavenumbers to interpolate onto
    """

    cur, conn = open_local(new_db)
    nwno = len(old_wno)
    for i in range(ntemp): 
        for m in molecules:
            opa_bundle = og_opacity.iloc[ i*nwno : (i+1) * nwno][m].values
            new_bundle = 10**(np.interp(new_wno,  old_wno, opa_bundle,right=-33,left=-33))
            insert(cur, conn, m, temperatures[i], new_bundle)

    conn.commit()
    conn.close()

if __name__ == '__main__':

    # For HWO, and JWST investigations of rocky planets.
    make_db(
        heliosk_dir='./', 
        data_dir='/home/nwogan/photochem_clima_data/photochem_clima_data/data', 
        min_wavelength=0.1, 
        max_wavelength=5.5, 
        new_R=15_000, 
        old_R=1e6
    )

    # For JWST MIRI investigations
    make_db(
        heliosk_dir='./', 
        data_dir='/home/nwogan/photochem_clima_data/photochem_clima_data/data', 
        min_wavelength=4.0, 
        max_wavelength=25.0, 
        new_R=10_000, 
        old_R=1e6
    )