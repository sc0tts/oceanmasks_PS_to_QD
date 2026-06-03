"""
Find where the NSIDC polar stereo grids project
  onto the latlon quarter degree grid

Usage:
    python find_psgrid_on_qdgrid.py

Example:

Approach:
    Generate a full-of-100s NH siconc field
    Reproject this onto QD grid
    Note where reprojected grid is nodata

    Generate a full-of-100s SH siconc field
    Reproject this onto QD grid
    Note where reprojected grid is nodata

    Read both grids in to create full-qd grid of missing PS data
"""

import sys
import subprocess
import numpy as np
from netCDF4 import Dataset
import imageio

def find_psgrid_on_qdgrid():
    """Create grids filled with values of 100 and morph onto the QD latlon grid"""
    # -----------------------------------------------------
    # Northern Hemisphere
    # -----------------------------------------------------
    grid100s_nh = np.zeros((448, 304), dtype=np.uint8)
    grid100s_nh[:] = 100

    # Write the raw binary data to a .dat file
    grid100s_nh_orig_dat = 'grid100s_psn25.dat'
    grid100s_nh.tofile(grid100s_nh_orig_dat)

    # Here is where we would dilate the concentration field to fill more land
    # Convert the .dat file to a portable gray map (.pgm)
    grid100s_nh_orig_pgm  = grid100s_nh_orig_dat.replace('.dat', '.pgm')
    subprocess.run([
        #'magick', 'convert',
        'magick', 
        '-extract', '304x448',
        '-size', '304x448',
        '-depth', '8',
        f'gray:{grid100s_nh_orig_dat}',
        f'{grid100s_nh_orig_pgm}'
    ])

    # Convert the .pgm file to a geotiff (.tif)
    grid100s_nh_orig_tif  = grid100s_nh_orig_pgm.replace('.pgm', '.tif')
    nh_epsg = 'epsg:3411'
    subprocess.run([
        'gdal_translate',
        '-q',
        '-of', 'GTiff',
        '-a_srs', f'{nh_epsg}',
        '-a_ullr', '-3850000', '5850000', '3750000', '-5350000',
        '-a_nodata', '255',
        f'{grid100s_nh_orig_pgm}',
        f'{grid100s_nh_orig_tif}'
    ])

    # Warp from polar stereo to latlon quarter degree
    # Note: when I tried endpoints: "0 -90 360 90",
    #  gdalwarp failed
    grid100s_nh_qd_tif = grid100s_nh_orig_tif.replace('.tif', '_qd.tif')
    subprocess.run([
        'gdalwarp',
        '-of', 'GTiff',
        '-t_srs', 'epsg:4326',
        '-tr', '0.25', '0.25',
        '-te', '-180', '-90', '180', '90',
        '-overwrite',
        '-r', 'nearest',
        f'{grid100s_nh_orig_tif}',
        f'{grid100s_nh_qd_tif}'
    ])

    # -----------------------------------------------------
    # Southern Hemisphere
    # -----------------------------------------------------
    grid100s_sh = np.zeros((332, 316), dtype=np.uint8)
    grid100s_sh[:] = 100

    # Write the raw binary data to a .dat file
    grid100s_sh_orig_dat = 'grid100s_pss25.dat'
    grid100s_sh.tofile(grid100s_sh_orig_dat)

    # Here is where we would dilate the concentration field to fill more land
    # Convert the .dat file to a portable gray map (.pgm)
    grid100s_sh_orig_pgm  = grid100s_sh_orig_dat.replace('.dat', '.pgm')
    subprocess.run([
        'magick', 
        '-extract', '316x332',
        '-size', '316x332',
        '-depth', '8',
        f'gray:{grid100s_sh_orig_dat}',
        f'{grid100s_sh_orig_pgm}'
    ])

    # Convert the .pgm file to a geotiff (.tif)
    grid100s_sh_orig_tif  = grid100s_sh_orig_pgm.replace('.pgm', '.tif')
    sh_epsg = 'epsg:3412'
    subprocess.run([
        'gdal_translate',
        '-q',
        '-of', 'GTiff',
        '-a_srs', f'{sh_epsg}',
        '-a_ullr', '-3950000', '4350000', '3950000', '-3950000',
        '-a_nodata', '255',
        f'{grid100s_sh_orig_pgm}',
        f'{grid100s_sh_orig_tif}'
    ])

    # Warp from polar stereo to latlon quarter degree
    # Note: when I tried endpoints: "0 -90 360 90",
    #  gdalwarp failed
    grid100s_sh_qd_tif = grid100s_sh_orig_tif.replace('.tif', '_qd.tif')
    subprocess.run([
        'gdalwarp',
        '-of', 'GTiff',
        '-t_srs', 'epsg:4326',
        '-tr', '0.25', '0.25',
        '-te', '-180', '-90', '180', '90',
        '-overwrite',
        '-r', 'nearest',
        f'{grid100s_sh_orig_tif}',
        f'{grid100s_sh_qd_tif}'
    ])

    # Now, read in both of those grids to create a single mask
    qd100s_nh = np.asarray(imageio.read(grid100s_nh_qd_tif).get_data(0))
    qd100s_sh = np.asarray(imageio.read(grid100s_sh_qd_tif).get_data(0))

    is_qd_on_polarstereo = np.zeros((720, 1440), dtype=np.uint8)
    is_qd_on_polarstereo[qd100s_nh < 200] = 100
    is_qd_on_polarstereo[qd100s_sh < 200] = 100

    # Write raw binary
    ofn = 'is_qd_on_polarstereo.dat'
    is_qd_on_polarstereo.tofile(ofn)
    print(f'Wrote: {ofn}')

    # Create version where longitude runs from 0 to 360
    is_qd_on_ps_0to360 = np.zeros((720, 1440), dtype=np.uint8)
    is_qd_on_ps_0to360[:, :720] = is_qd_on_polarstereo[:, 720:]
    is_qd_on_ps_0to360[:, 720:] = is_qd_on_polarstereo[:, :720]
    ofn = 'is_qd_on_ps_0to360.dat'
    is_qd_on_ps_0to360.tofile(ofn)
    print(f'Wrote: {ofn}')
    breakpoint()



if __name__ == '__main__':
    find_psgrid_on_qdgrid()
