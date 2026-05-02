"""mask_from_raw_ps.py

Extract a land mask from an NSIDC polar stereo grid

# For CDRv5,
#      50: ocean (considered water)
#      75: lake (considered land)
#     200: coast (considered land)
#     250: land

The expectation is that all ubyte values other than 200 or 250 are ocean
"""

import sys
import numpy as np

# Sea ice concentration file name (fn_siconc) is the first argument
fn_siconc = sys.argv[1]

# Land mask file name (output, fn_landmask) is the second argument
fn_landmask = sys.argv[2]

# Water mask file name (output, fn_watermask) is the second argument
fn_watermask = sys.argv[3]

# Do not overwrite the input file
assert fn_siconc != fn_landmask
assert fn_siconc != fn_watermask

# Land and water masks are different
assert fn_landmask != fn_watermask

raw = np.fromfile(fn_siconc, dtype=np.uint8)

# Only "ocean" is "water"
is_water = raw == 50  # Only "ocean" is "water"
is_land = ~is_water
is_land.tofile(fn_landmask)
print(f'Extracted landmask from:\n  {fn_siconc}\nand wrote to:\n  {fn_landmask}')

# Convert to a value of 100 so it is easier to see in a plot of the raw binary values
is_water = is_water.astype(np.uint8)
is_water[is_water > 0] = 100
is_water.tofile(fn_watermask)
print(f'Extracted watermask from:\n  {fn_siconc}\nand wrote to:\n  {fn_watermask}')
