"""extract_orig_ice_mask.py

Extract the original ice_mask field from the OISST netCDF file

Sample usage:
    python extract_orig_ice_mask.py oisst_v3_ice_mask_1993-2024.nc oisst_ice_mask_vals_01-36.dat
"""

import sys
import numpy as np
from netCDF4 import Dataset  # pylint: disable=E0611;  (pylint is wrong)

# Sea ice concentration file name (fn_siconc) is the first argument
ncfn_oisst = sys.argv[1]

# Land mask file name (output, fn_landmask) is the second argument
fn_mask = sys.argv[2]

# Do not overwrite the input file
assert ncfn_oisst != fn_mask


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

assert np.min(ice_mask) >= 0
assert np.max(ice_mask) < 256

ice_mask = ice_mask.astype(np.uint8)

ice_mask.tofile(fn_mask)
print(f'Wrote: {fn_mask}  dtype={ice_mask.dtype}  shape={ice_mask.shape}')
