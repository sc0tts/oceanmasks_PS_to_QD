#!/bin/bash
#
# process_iceshelves.sh
#
#
# Note: GeoTransform values are wrong for grids in 0780 that are not PS-N25
# ------------------------------------------------------------------ #
#
# NH sea_ice_region_surface_mask coding:
#
# ------------------------------------------------------------------ #

./correct_nsidc0780_geotransforms.sh

# This expands ice shelf onto "land" in the polar stereo grid
#   Saves the new polar-stereo surface mask to: newmask_pss3125.nc
#     from
#       mask_psn3125.nc
#     to
#       newmask_psn3125.nc
# Note:  41 iterations works
python create_dilated_iceshelf_pss25.py 41

# NH
in_nh=mask_psn3125.nc
in_nh_gdalvar="NETCDF:./${in_nh}:sea_ice_region_surface_mask"
out_nh=nh_surfmask.tif
gdalwarp -of GTiff -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest -srcnodata 0 -dstnodata 0 "$in_nh_gdalvar" $out_nh

# SH
#in_sh=mask_pss3125.nc
in_sh=newmask_pss3125.nc
in_sh_gdalvar="NETCDF:./${in_sh}:sea_ice_region_NASA_surface_mask"
out_sh=sh_surfmask.tif
gdalwarp -of GTiff -s_srs epsg:3412 -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest -srcnodata 0 -dstnodata 0 "$in_sh_gdalvar" $out_sh


python add_iceshelves_to_qd.py


