#!/bin/bash
#
# correct_nsidc0780_geotransforms.sh
#
#
# Note: GeoTransform values are wrong for grids in 0780 that are not PS-N25
# ------------------------------------------------------------------ #
#
# NH sea_ice_region_surface_mask coding:
#
# ------------------------------------------------------------------ #

# Northern Hemisphere...
in_nh_orig="/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-N3.125km_v1.0.nc"
in_nh=mask_psn3125.nc
cp -v $in_nh_orig $in_nh

nh_geotransform='-3850000 3125 0 5850000 0 -3125 '
ncatted -O -a GeoTransform,crs,o,c,"$nh_geotransform" $in_nh
ncatted -O -a semi_major_axis,crs,o,f,6378273. $in_nh
ncatted -O -a inverse_flattening,crs,o,f,298.279411123064 $in_nh
ncatted -O -a crs_wkt,crs,d,, $in_nh
ncatted -O -a spatial_ref,crs,d,, $in_nh

echo "Wrote: ${in_nh}"


# Southern Hemisphere...
in_sh_orig="/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-S3.125km_v1.0.nc"
in_sh=mask_pss3125.nc
cp -v $in_sh_orig $in_sh

sh_geotransform='-3950000 3125 0 4350000 0 -3125 '
ncatted -O -a GeoTransform,crs,o,c,"$sh_geotransform" $in_sh
ncatted -O -a semi_major_axis,crs,o,f,6378273. $in_sh
ncatted -O -a inverse_flattening,crs,o,f,298.279411123064 $in_sh
ncatted -O -a crs_wkt,crs,d,, $in_sh
ncatted -O -a spatial_ref,crs,d,, $in_sh


echo "Wrote: ${in_sh}"
