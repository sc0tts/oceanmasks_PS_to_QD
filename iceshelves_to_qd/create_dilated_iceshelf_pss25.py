"""
Create a dilated-onto-land iceshelf mask

The approach is to:
    Read in the SH surface mask field
    Determine the initial:
      is_land
      is_ocean
      is_iceshelf
    Then dilate is_ocean and is_iceshelf onto the land
"""

import sys
import shutil
import xarray as xr
import numpy as np
from netCDF4 import Dataset
from scipy.signal import convolve2d


def dilate_iceshelves(ncfn, newfn, n_dilations):
    """Dilate the ice shelves onto land, preferring ocean"""
    # Copy the orig to the new
    shutil.copyfile(ncfn, newfn)

    with Dataset(ncfn) as ds:
        surfmask = np.asarray(ds.variables['sea_ice_region_NASA_surface_mask'])

    print('check surfmask')
    ofn = 'surfmask_orig_2528x2656.dat'
    surfmask.tofile(ofn)
    print(f'Wrote: {ofn}')

    # Loop dilations
    is_iceshelf = surfmask == 34
    # Note: For this Southern Hemisphere mask, most of the "land" is labeled "ice-on-land"
    is_land = (surfmask == 30) | (surfmask == 32) | (surfmask == 33)  # land, lake, or ice-on-land
    is_ocean = (surfmask < 30) | (surfmask == 35)  # Open ocean, named ocean, or disconnected ocean

    kernel_plus = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ], dtype=np.uint8)

    kernel_square = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ], dtype=np.uint8)

    is_dilatable = is_land.copy()
    is_exp_iceshelf = is_iceshelf.copy()
    is_exp_ocean = is_ocean.copy()
    for n in range(n_dilations):
        if n < 2:
            kernel = kernel_plus
        else:
            kernel = kernel_square
        # First, dilate the ocean onto the dilatable grid cells
        convolved = convolve2d(is_exp_ocean, kernel, mode='same', boundary='symm')
        is_exp_ocean_new = (is_exp_ocean | (convolved > 0)) & is_dilatable
        print(f' Dilation {n}: Expanded ocean by {np.sum(np.where(is_exp_ocean_new, 1, 0))} grid cells')
        is_exp_ocean[is_exp_ocean_new] = True
        is_dilatable[is_exp_ocean_new] = False

        # Next, dilate the ice shelf onto the dilatable grid cells
        convolved = convolve2d(is_exp_iceshelf, kernel, mode='same', boundary='symm')
        is_exp_iceshelf_new = (is_exp_iceshelf | (convolved > 0)) & is_dilatable
        print(f' Dilation {n}: Expanded iceshelf by {np.sum(np.where(is_exp_iceshelf_new, 1, 0))} grid cells')
        is_exp_iceshelf[is_exp_iceshelf_new] = True
        is_dilatable[is_exp_iceshelf_new] = False

    new_surfmask = surfmask.copy()
    new_surfmask[is_land & is_exp_ocean] = 47
    new_surfmask[is_land & is_exp_iceshelf] = 60
    ofn = f'surfmask_new_2528x2656_{n_dilations}.dat'
    new_surfmask.tofile(ofn)
    print(f'Wrote: {ofn}')

    is_now_iceshelf = new_surfmask == 60
    n_now_iceshelf = np.sum(np.where(is_now_iceshelf, 1, 0))
    print(f'Number of points newly considered iceshelf: {n_now_iceshelf}')

    # update the new file
    dsnew = Dataset(newfn, 'r+')
    arr = np.asarray(dsnew['sea_ice_region_NASA_surface_mask'])
    arr[is_now_iceshelf] = 34
    dsnew['sea_ice_region_NASA_surface_mask'][:] = arr[:]
    dsnew.close()
    print(f'Wrote: {newfn}')


if __name__ == '__main__':
    # Note: The GeoTransform in the original NSIDC-0780 files is incorrect
    # The corrected file is in this directory as mask_pss3125.nc
    ncfn = 'mask_pss3125.nc'
    newfn = 'newmask_pss3125.nc'

    n_dilations = 5
    try:
        n_dilations = int(sys.argv[1])
    except IndexError:
        print(f'Using default number of dilations: {n_dilations}')

    dilate_iceshelves(ncfn, newfn, n_dilations)
