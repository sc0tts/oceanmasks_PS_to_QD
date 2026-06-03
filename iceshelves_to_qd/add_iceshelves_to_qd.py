"""Add the ice shelf values to the OISST QD grid

Usage:
    python add_iceshelves_to_qd.py

Reads in:
    nh_surfmask.tif
    sh_surfmask.tif
    oisst_v3_ice_mask_1993-2024_corrected.nc

"""

import numpy as np
import imageio
from netCDF4 import Dataset
import shutil


def overlay_iceshelves(ncfn, nhfn, shfn, outfn):
    """Direct overlay of ice shelf values onto QD grid"""
    # Read in the QD land mask
    # ice_mask in OISST is
    #   flipped relative to UL-origin image convention
    #   has left-to-right of 0 to 360 deg instead of -180 to 180 deg
    with Dataset(ncfn) as ds:
        qdmask_0to360 = np.flipud(np.asarray(ds.variables['ice_mask']))

    xdim = 1440
    ydim = 720
    qdmask = np.zeros(qdmask_0to360.shape, dtype=np.uint8)
    qdmask[:, :720] = qdmask_0to360[:, 720:]
    qdmask[:, 720:] = qdmask_0to360[:, :720]

    ofn = 'qdmask_1440x720.dat'
    qdmask.tofile(ofn)
    print(f'  Wrote: {ofn}')

    # Read in the Southern Hemisphere Surface type
    arr_iceshelf_sh = np.asarray(imageio.read(shfn).get_data(0))
    arr_iceshelf_sh.tofile('arr_iceshelf_sh.dat')
    print('check arr_iceshelf_sh')

    is_sh_iceshelf = arr_iceshelf_sh == 34
    is_qdmask_sh_ocean = (qdmask >= 25) & (qdmask <= 36)

    is_sh_overlay = is_sh_iceshelf & is_qdmask_sh_ocean
    qdmask[is_sh_overlay] = 40

    ofn = 'new_qdmask_1440x720.dat'
    qdmask.tofile(ofn)
    print(f'  Wrote: {ofn}')

    # Now, need to put these new values into the new field
    # Re project to flipped 0-360
    new_qdmask_0to360 = np.zeros(qdmask_0to360.shape, dtype=np.uint8)
    new_qdmask_0to360[:, :720] = qdmask[:, 720:]
    new_qdmask_0to360[:, 720:] = qdmask[:, :720]
    # new_qdmask_0to360 = np.flipud(new_qdmask_0to360)

    # Copy the input file to the output file
    shutil.copyfile(ncfn, outfn)
    dsnew = Dataset(outfn, 'r+')
    dsnew['ice_mask'][:] = new_qdmask_0to360[:]
    dsnew.close()
    print(f'Wrote: {outfn}')

    breakpoint()

if __name__ == '__main__':
    oisst_ncfn = '../oisst_v3_ice_mask_1993-2024_corrected.nc'
    nh_tiffn = './nh_surfmask.tif'
    sh_tiffn = './sh_surfmask.tif'

    output_ncfn = '../oisst_v3_ice_mask_1993-2024_corr_iceshelves.nc'

    overlay_iceshelves(oisst_ncfn, nh_tiffn, sh_tiffn, output_ncfn)
