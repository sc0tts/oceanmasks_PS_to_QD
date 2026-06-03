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

#in_nh_gdalvar_orig="NETCDF:/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-N3.125km_v1.0.nc:sea_ice_region_surface_mask"

in_nh_orig="/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-N3.125km_v1.0.nc"
in_nh=mask_psn3125.nc
cp -v $in_nh_orig $in_nh

nh_geotransform="'-3850000 3125 0 5850000 0 -3125 '"
ncatted -O -a GeoTransform,crs,o,c,"$nh_geotransform" $in_nh

in_nh_gdalvar="NETCDF:./${in_nh}:sea_ice_region_surface_mask"
out_nh=nh_surfmask.tif
gdalwarp -of GTiff -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest -srcnodata 0 -dstnodata 0 "$in_nh_gdalvar" $out_nh


# SH
#in_sh_gdalvar_orig="NETCDF:/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-S3.125km_v1.0.nc:sea_ice_region_NASA_surface_mask"

in_sh_orig="/data/nsidc0780/netcdf/NSIDC-0780_SeaIceRegions_PS-S3.125km_v1.0.nc"

in_sh=mask_pss3125.nc
cp -v $in_sh_orig $in_sh

sh_geotransform="'-3950000 3125 0 4350000 0 -3125 '"
ncatted -O -a GeoTransform,crs,o,c,"$sh_geotransform" $in_sh

in_sh_gdalvar="NETCDF:./${in_sh}:sea_ice_region_NASA_surface_mask"
out_sh=sh_surfmask.tif
gdalwarp -of GTiff -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest -srcnodata 0 -dstnodata 0 "$in_sh_gdalvar" $out_sh


<<NH_encoding
 0  ocean_no_region_specified
 1  central_arctic
 2  beaufort_sea
 3  chukchi_sea
 4  east_siberian_sea
 5  laptev_sea
 6  kara_sea
 7  barents_sea
 8  east_greenland_sea
 9  baffin_bay_and_labrador_seas
 10 gulf_of_st_lawrence
 11 hudson_bay
 12 canadian_archipelago
 13 bering_sea
 14 sea_of_okhotsk
 15 sea_of_japan
 16 bohai_and_yellow_seas
 17 baltic_sea
 18 gulf_of_alaska

 30 land
 32 fresh_free_water
 33 ice_on_land

 34 floating_ice_shelf

 35 ocean_disconnected
NH_encoding
    
<<SH_encoding
 0  ocean_no_region_specified
 1  weddell_sea
 2  indian_ocean
 3  south_pacific_ocean
 4  ross_sea
 5  amundsen_and_bellingshausen_seas

 30 land
 32 fresh_free_water
 33 ice_on_land

 34 floating_ice_shelf

 35 ocean_disconnected
SH_encoding
