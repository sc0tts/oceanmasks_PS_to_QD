"""
Reproject CDR siconc so it fills the quarter-degree grid

Usage:
    python reproject_siconc <nfn> <sfn>
  where
    nfn: northern hemisphere file name
    sfn: southern hemisphere file name

Example:
    python reproject_siconc sic_psn25_20260501_am2_v06r00.nc sic_pss25_20260501_am2_v06r00.nc

Approach:
    Read NH siconc
    Dilate NH siconc field sufficient to fill QD grid
    Reproject dilated NH siconc to QD grid

    Read SH siconc
    Dilate SH siconc field sufficient to fill QD grid
    Reproject dilated SH siconc to QD grid

    Read QD ocean mask
    Pre-fill with missing values
    Fill with off-grid values
    Read in dilated/reprojected NH, SH values
"""

import sys
import subprocess
from scipy.signal import convolve2d
import numpy as np
from netCDF4 import Dataset
import imageio


def reproject_siconc(nfn, sfn):
    """Reproject the north and south siconc fields onto the QD field"""
    # -----------------------------------------------------
    # Northern Hemisphere
    # -----------------------------------------------------
    dsn = Dataset(nfn)
    dsn.set_auto_maskandscale(False)
    siconc_nh = np.squeeze(np.asarray(dsn['cdr_seaice_conc']))
    is_unusual_value = (siconc_nh > 100) & (siconc_nh != 255)
    n_unusual_values = np.sum(np.where(is_unusual_value, 1, 0))
    if n_unusual_values > 0:
        print(f'WARNING: Found {n_unusual_values} in {nfn}\n  Setting to missing')
        siconc_nh[is_unusual_value] = 255

    # Write the raw binary data to a .dat file
    siconc_nh_orig_dat = 'siconc_psn25_orig.dat'
    siconc_nh.tofile(siconc_nh_orig_dat)

    # Here is where we would dilate the concentration field to fill more land
    # Update siconc_nh with average values
    siconc_nh = siconc_nh.astype(np.float32)
    n_nh_dilations = 10
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    for n in range(n_nh_dilations):
        is_water = siconc_nh <= 100
        water_or_not = is_water.astype(np.uint8)
        only_siconc = siconc_nh.copy()
        only_siconc[only_siconc > 100] = 0
        num_val = convolve2d(water_or_not, kernel, mode='same', boundary='symm')
        sum_val = convolve2d(only_siconc, kernel, mode='same', boundary='symm')
        has_avg_val = num_val > 0
        num_val[num_val == 0] = 1
        avg_val = np.divide(sum_val, num_val)
        is_new_value = has_avg_val & ~is_water
        siconc_nh[is_new_value] = avg_val[is_new_value]

    siconc_nh = np.round(siconc_nh).astype(np.uint8)

    # Write the raw binary data to a .dat file
    siconc_nh_dat = 'siconc_psn25.dat'
    siconc_nh.tofile(siconc_nh_dat)

    # Convert the .dat file to a portable gray map (.pgm)
    siconc_nh_orig_pgm  = siconc_nh_dat.replace('.dat', '.pgm')
    subprocess.run([
        'magick', 
        '-extract', '304x448',
        '-size', '304x448',
        '-depth', '8',
        f'gray:{siconc_nh_dat}',
        f'{siconc_nh_orig_pgm}'
    ])

    # Convert the .pgm file to a geotiff (.tif)
    siconc_nh_orig_tif  = siconc_nh_orig_pgm.replace('.pgm', '.tif')
    nh_epsg = 'epsg:3411'
    subprocess.run([
        'gdal_translate',
        '-q',
        '-of', 'GTiff',
        '-a_srs', f'{nh_epsg}',
        '-a_ullr', '-3850000', '5850000', '3750000', '-5350000',
        '-a_nodata', '255',
        f'{siconc_nh_orig_pgm}',
        f'{siconc_nh_orig_tif}'
    ])

    # Warp from polar stereo to latlon quarter degree
    # Note: when I tried endpoints: "0 -90 360 90",
    #  gdalwarp failed
    siconc_nh_qd_tif = siconc_nh_orig_tif.replace('.tif', '_qd.tif')
    subprocess.run([
        'gdalwarp',
        '-of', 'GTiff',
        '-t_srs', 'epsg:4326',
        '-tr', '0.25', '0.25',
        '-te', '-180', '-90', '180', '90',
        '-overwrite',
        '-r', 'nearest',
        f'{siconc_nh_orig_tif}',
        f'{siconc_nh_qd_tif}'
    ])

    # -----------------------------------------------------
    # Southern Hemisphere
    # -----------------------------------------------------
    dss = Dataset(sfn)
    dss.set_auto_maskandscale(False)
    siconc_sh = np.squeeze(np.asarray(dss['cdr_seaice_conc']))
    is_unusual_value = (siconc_sh > 100) & (siconc_sh != 255)
    n_unusual_values = np.sum(np.where(is_unusual_value, 1, 0))
    if n_unusual_values > 0:
        print(f'WARNING: Found {n_unusual_values} in {sfn}\n  Setting to missing')
        siconc_nh[is_unusual_value] = 255

    # Write the raw binary data to a .dat file
    siconc_sh_orig_dat = 'siconc_pss25_orig.dat'
    siconc_sh.tofile(siconc_sh_orig_dat)

    # Update siconc_sh with average values
    siconc_sh = siconc_sh.astype(np.float32)
    n_sh_dilations = 7
    # Check with:  np.sum(np.where(qd_siconc == 255, 1, 0))
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    for n in range(n_sh_dilations):
        is_water = siconc_sh <= 100
        water_or_not = is_water.astype(np.uint8)
        only_siconc = siconc_sh.copy()
        only_siconc[only_siconc > 100] = 0
        num_val = convolve2d(water_or_not, kernel, mode='same', boundary='symm')
        sum_val = convolve2d(only_siconc, kernel, mode='same', boundary='symm')
        has_avg_val = num_val > 0
        num_val[num_val == 0] = 1  # Don't divide by zero
        avg_val = np.divide(sum_val, num_val)
        is_new_value = has_avg_val & ~is_water
        siconc_sh[is_new_value] = avg_val[is_new_value]

    siconc_sh = np.round(siconc_sh).astype(np.uint8)

    # Write the raw binary data to a .dat file
    siconc_sh_dat = 'siconc_pss25.dat'
    siconc_sh.tofile(siconc_sh_dat)

    # Convert the .dat file to a portable gray map (.pgm)
    siconc_sh_orig_pgm  = siconc_sh_dat.replace('.dat', '.pgm')
    subprocess.run([
        'magick', 
        '-extract', '316x332',
        '-size', '316x332',
        '-depth', '8',
        f'gray:{siconc_sh_dat}',
        f'{siconc_sh_orig_pgm}'
    ])

    # Convert the .pgm file to a geotiff (.tif)
    siconc_sh_orig_tif  = siconc_sh_orig_pgm.replace('.pgm', '.tif')
    sh_epsg = 'epsg:3412'
    subprocess.run([
        'gdal_translate',
        '-q',
        '-of', 'GTiff',
        '-a_srs', f'{sh_epsg}',
        '-a_ullr', '-3950000', '4350000', '3950000', '-3950000',
        '-a_nodata', '255',
        f'{siconc_sh_orig_pgm}',
        f'{siconc_sh_orig_tif}'
    ])

    # Warp from polar stereo to latlon quarter degree
    # Note: when I tried endpoints: "0 -90 360 90",
    #  gdalwarp failed
    siconc_sh_qd_tif = siconc_sh_orig_tif.replace('.tif', '_qd.tif')
    subprocess.run([
        'gdalwarp',
        '-of', 'GTiff',
        '-t_srs', 'epsg:4326',
        '-tr', '0.25', '0.25',
        '-te', '-180', '-90', '180', '90',
        '-overwrite',
        '-r', 'nearest',
        f'{siconc_sh_orig_tif}',
        f'{siconc_sh_qd_tif}'
    ])

    nh_siconc = np.asarray(imageio.read(siconc_nh_qd_tif).get_data(0))
    sh_siconc = np.asarray(imageio.read(siconc_sh_qd_tif).get_data(0))

    qd100s_dat = 'is_qd_on_polarstereo.dat'
    qd100s = np.fromfile(qd100s_dat, dtype=np.uint8).reshape(720, 1440)
    is_on_polarstereo = qd100s > 0

    # Read in the QD ice_mask
    qd_icemask_ncfn = '../oisst_v3_ice_mask_1993-2024_corr_iceshelves.nc'
    with Dataset(qd_icemask_ncfn) as ds:
        ice_mask_0to360 = np.asarray(ds['ice_mask'])
    ofn = 'icemask_0to360.dat'
    ice_mask_0to360.tofile(ofn)
    print(f'Wrote: {ofn}')

    ice_mask = np.zeros((720, 1440), dtype=np.uint8)
    ice_mask[:, 720:] = ice_mask_0to360[:, :720]
    ice_mask[:, :720] = ice_mask_0to360[:, 720:]

    ofn = 'icemask.dat'
    ice_mask.tofile(ofn)
    print(f'Wrote: {ofn}')

    is_ice_shelf = ice_mask == 40
    is_icemask_water = (ice_mask > 0) & ~is_ice_shelf

    # Determine (in)valid latitude range by inspection
    is_outside_valid_lats = np.zeros((720, 1440), dtype=bool)
    is_outside_valid_lats[228:491+1, :] = True

    is_icemask_land = ~is_icemask_water & ~is_outside_valid_lats & ~is_ice_shelf

    # Fill the QD siconc grid
    #   0-100: siconc from CDR
    #   150: Land
    #   170: Lakes (hand-specified)
    #   200: Ocean, but ice shelf
    #   220: QD ocean, but not on polarstereo grids
    #   230: On polarstereo, but outside QD valid latitude range
    #   240: QD outside valid latitude range
    #   255: Not-yet-set value

    ivals, jvals = np.meshgrid(range(1440), range(720))
    is_great_lakes = (ivals > 351) & (ivals < 416) & (jvals > 163) & (jvals < 194) & ~is_icemask_land

    is_russian_lake = (ivals > 839) & (ivals < 851) & (jvals > 112) & (jvals < 121) & ~is_icemask_land

    is_lakes = is_great_lakes | is_russian_lake


    qd_siconc = np.zeros((720, 1440), dtype=np.uint8)

    qd_siconc[:, :] = 255  # default
    qd_siconc[is_outside_valid_lats] = 240  # bad lat
    qd_siconc[is_outside_valid_lats & is_on_polarstereo] = 230  # bad lat, but on PS grid
    qd_siconc[is_ice_shelf] = 200  # ice shelf
    qd_siconc[is_icemask_land] = 150  # Land
    qd_siconc[is_lakes] = 170  # Land
    qd_siconc[~is_outside_valid_lats & ~is_on_polarstereo] = 220  # ocean, but off PS grid


    is_from_nh_siconc = is_on_polarstereo & is_icemask_water & (nh_siconc <= 100)
    is_from_sh_siconc = is_on_polarstereo & is_icemask_water & (sh_siconc <= 100)
    qd_siconc[is_from_nh_siconc] = nh_siconc[is_from_nh_siconc]
    qd_siconc[is_from_sh_siconc] = sh_siconc[is_from_sh_siconc]

    ofn = 'qd_siconc.dat'
    qd_siconc.tofile(ofn)
    print(f'Wrote: {ofn}')


if __name__ == '__main__':
    # Read the north 
    nfn = sys.argv[1]
    sfn = sys.argv[2]

    reproject_siconc(nfn, sfn)
