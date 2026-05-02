#!/bin/bash
#
# process_landmasks.sh
#
# Analyze files relevant to reprojecting sea ice concentrations on
# NSIDC 25km polar stereo grids per the CDRv6 ancillary files
# to the NOAA OISST 1/4-degree global grid

# Global definitions
ncfn_dummy=dummy.nc

# ------------------------------------------------------------------ #
# Extract the land mask for the NSIDC 25km NH polar stereo siconc grid
# ------------------------------------------------------------------ #
ncfn_psn25=./cdr_ancillary/G02202-ancillary-psn25-v06r00.nc
sicvar_psn25=surface_type
rawfn_psn25=rawmask_psn25.dat

# Extract the siconc field from a sample data file
ncks -C -O -v ${sicvar_psn25} -b ${rawfn_psn25} ${ncfn_psn25} ${ncfn_dummy}
echo "Extracted ${rawfn_psn25} from ${ncfn_psn25}"

# Here, the file "rawmask_psn25.dat" is a raw binary file
#   of size 304x448 (136,192 bytes) 
# For CDRv5, 
#      50: ocean (considered water)
#      75: lake (considered water)
#     200: coast (considered land)
#     250: land

fn_rawland_psn25=landmask_psn25.dat
fn_rawwater_psn25=watermask_psn25.dat

python mask_from_cdranc.py ${rawfn_psn25} ${fn_rawland_psn25} ${fn_rawwater_psn25}

# ------------------------------------------------------------------ #
# Extract the land mask for the NSIDC 25km SH polar stereo siconc grid
# ------------------------------------------------------------------ #
ncfn_pss25=./cdr_ancillary/G02202-ancillary-pss25-v06r00.nc
sicvar_pss25=surface_type
rawfn_pss25=rawmask_pss25.dat

# Extract the siconc field from a sample data file
ncks -C -O -v ${sicvar_pss25} -b ${rawfn_pss25} ${ncfn_pss25} ${ncfn_dummy}
echo "Extracted ${rawfn_pss25} from ${ncfn_pss25}"

# Here, the file "rawmask_pss25.dat" is a raw binary file
#   of size 316x332 (104,912 bytes) 
fn_rawland_pss25=landmask_pss25.dat
fn_rawwater_pss25=watermask_pss25.dat

python mask_from_cdranc.py ${rawfn_pss25} ${fn_rawland_pss25} ${fn_rawwater_pss25}

# Extract the land and water masks from the oisst file

python extract_masks_qdgrid.py ./oisst_orig/oisst_v3_ice_mask_1993-2024.nc oisst_land.dat oisst_water.dat


# --------------------------------------------------- #
# Now, create  geotiffs of the above raw binary files #
# --------------------------------------------------- #
# Water for psn25
fn_raw=${fn_rawwater_psn25}
fn_pgm=${fn_raw//.dat/.pgm}
fn_tif=${fn_raw//.dat/.tif}
convert -extract 304x448 -size 304x448  -depth 8 gray:${fn_raw} ${fn_pgm}
gdal_translate -q -of GTiff -a_srs epsg:3411 -a_ullr -3850000 5850000 3750000 -5350000 -a_nodata 0 ${fn_pgm} ${fn_tif}
rm ${fn_pgm}
fn_tifwater_psn25=${fn_tif}
echo "Created ${fn_tifwater_psn25}"

# Water for pss25
fn_raw=${fn_rawwater_pss25}
fn_pgm=${fn_raw//.dat/.pgm}
fn_tif=${fn_raw//.dat/.tif}
convert -extract 316x332 -size 316x332  -depth 8 gray:${fn_raw} ${fn_pgm}
gdal_translate -q -of GTiff -a_srs epsg:3412 -a_ullr -3950000 4350000 3950000 -3950000 -a_nodata 0 ${fn_pgm} ${fn_tif}
rm ${fn_pgm}
fn_tifwater_pss25=${fn_tif}
echo "Created ${fn_tifwater_pss25}"

# Now, re-project these water masks to qd-latlon
# NH
fntif_water_psn25_on_qd=watermask_psn25_on_qd.tif
gdalwarp -of GTiff -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest $fn_tifwater_psn25 $fntif_water_psn25_on_qd
echo "Wrote: $fntif_water_psn25_on_qd"

# SH
fntif_water_pss25_on_qd=watermask_pss25_on_qd.tif
gdalwarp -of GTiff -t_srs epsg:4326 -tr 0.25 0.25 -te -180 -90 180 90 -overwrite -r nearest $fn_tifwater_pss25 $fntif_water_pss25_on_qd
echo "Wrote: $fntif_water_pss25_on_qd"

# Create geotiff of the OISST water (ocean) mask
fn_raw_water_oisst=oisst_water.dat
fn_pgm_water_oisst=watermask_oisst_on_qd.pgm
fn_tif_water_oisst=watermask_oisst_on_qd.tif
convert -extract 1440x720 -size 1440x720  -depth 8 gray:${fn_raw_water_oisst} ${fn_pgm_water_oisst}
gdal_translate -q -of GTiff -a_srs epsg:4326 -a_ullr -180 90 180 -90 -a_nodata 0 ${fn_pgm_water_oisst} ${fn_tif_water_oisst}
rm ${fn_pgm_water_oisst}
echo "Created ${fn_tif_water_oisst}"
