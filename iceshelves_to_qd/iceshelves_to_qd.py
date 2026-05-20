"""iceshelves_to_qd.py

Regrid 3.125km grid to QD

Usage:
    python iceshelves_to_qd.py
"""

#pylint: disable=C0103; invalid-name
#pylint: disable=C0301; Line too long (line-too-long)

#pylint: disable=R0914; Too many local variables (too-many-locals)
#pylint: disable=R0915; Too many statements (too-many-statements)

#pylint: disable=W0104; Statement seems to have no effect (pointless-statement)
#pylint: disable=W0611; no-name-in-module
#pylint: disable=W0621; Redefining name
#pylint: disable=W0612; Unused variable
#pylint: disable=W0613; Unused argument
#pylint: disable=W1515; Breakpoints

# flake8: noqa

from netCDF4 import Dataset  # pylint: disable=E0611;  (pylint is wrong)
import imageio


# Note: the 
nh_nc = '/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-N3.125km_v1.0.nc'
sh_nc = '/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-S3.125km_v1.0.nc'

nh_gdalvar = 'NETCDF:"/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-N3.125km_v1.0.nc":sea_ice_region_surface_mask'

ds_nh = Dataset(nh_nc)
ds_sh = Dataset(sh_nc)

# For both NH and SH: ice shelves are encoded as "34"
