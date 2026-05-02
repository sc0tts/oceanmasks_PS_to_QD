"""extract_masks_qdgrid.py

Extract land and water masks from OISST quarter-degree lat/lon grid

Sample usage:
    python extract_masks_qdgrid.py oisst_v3_ice_mask_1993-2024.nc oisst_land.dat oisst_water.dat
"""

import sys
import numpy as np
from netCDF4 import Dataset  # noqa

# Sea ice concentration file name (fn_siconc) is the first argument
ncfn_oisst = sys.argv[1]

# Land mask file name (output, fn_landmask) is the second argument
fn_landmask = sys.argv[2]

# Water mask file name (output, fn_watermask) is the second argument
fn_watermask = sys.argv[3]

# Do not overwrite the input file
assert ncfn_oisst != fn_landmask
assert ncfn_oisst != fn_watermask

# Land and water masks are different
assert fn_landmask != fn_watermask

# Read the mask field from the netCDF file
# Note: because the valid_min and valid_max are wrong, ignore auto-masking/scaling
ds_oisst = Dataset(ncfn_oisst)
ds_oisst.set_auto_maskandscale(False)
ice_mask_0to360 = ds_oisst['ice_mask'].__array__()

# Convert the array to standard representation
# have origin in upper-left of map
ice_mask_0to360 = np.flipud(ice_mask_0to360)

# center on Greenwich rather than on -180/180
ice_mask = ice_mask_0to360.copy()
ice_mask[:, :720] = ice_mask_0to360[:, 720:]
ice_mask[:, 720:] = ice_mask_0to360[:, :720]

is_land = ice_mask == 0
is_land.tofile(fn_landmask)
print(f'Extracted landmask from:\n  {ncfn_oisst}\nand wrote to:\n  {fn_landmask}')

is_water = ~is_land
is_water = is_water.astype(np.uint8)
is_water[is_water > 0] = 100
is_water.tofile(fn_watermask)
print(f'Extracted watermask from:\n  {ncfn_oisst}\nand wrote to:\n  {fn_watermask}')
