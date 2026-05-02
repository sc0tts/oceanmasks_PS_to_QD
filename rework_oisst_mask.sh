#!/bin/bash
#
#Eg compare to:
#  https://gpm.nasa.gov/data/directory/imerg-tmpa-land-sea-masks
#    
#  https://ldas.gsfc.nasa.gov/gldas/vegetation-class-mask
#  ...but this excludes Antarctica (!)
#
# netcdf oisst_v3_ice_mask_1993-2024 {
# dimensions:
# 	lat = 720 ;
# 	lon = 1440 ;
# variables:
# 	float ice_mask(lat, lon) ;
# 		ice_mask:long_name = "Sea ice capability mask" ;
# 		ice_mask:units = "1" ;
# 		ice_mask:valid_min = 0. ;
# 		ice_mask:valid_max = 1. ;
# 		ice_mask:flag_values = 0., 1. ;
# 		ice_mask:flag_meanings = "no_ice_capability ice_capable" ;
# 		ice_mask:description = "Climatological mask indicating regions capable of sea ice formation. Values >= 0.5 indicate ice-capable regions, < 0.5 indicate non-ice regions." ;
# 	double lon(lon) ;
# 		lon:_FillValue = NaN ;
# 		lon:long_name = "Longitude" ;
# 		lon:units = "degrees_east" ;
# 		lon:axis = "X" ;
# 		lon:standard_name = "longitude" ;
# 		lon:valid_min = 0.125 ;
# 		lon:valid_max = 359.875 ;
# 	double lat(lat) ;
# 		lat:_FillValue = NaN ;
# 		lat:long_name = "Latitude" ;
# 		lat:units = "degrees_north" ;
# 		lat:axis = "Y" ;
# 		lat:standard_name = "latitude" ;
# 		lat:valid_min = -89.875 ;
# 		lat:valid_max = 89.875 ;
# 
# // global attributes:
# 		:title = "NOAA OISST v3 Sea Ice Capability Mask" ;
# 		:institution = "NOAA National Centers for Environmental Information (NCEI)" ;
# 		:source = "OISST v3 ice_flags_mask.dat" ;
# 		:history = "Created from binary file on 2025-07-20 03:15:37 by convert_mask_final.py" ;
# 		:references = "Reynolds, R.W., et al., 2007: Daily High-Resolution-Blended Analyses for Sea Surface Temperature. J. Climate, 20, 5473-5496. https://doi.org/10.1175/2007JCLI1824.1" ;
# 		:comment = "This climatological mask indicates regions where sea ice can potentially form. It is used in the OISST v3 algorithm to constrain ice concentration data assimilation. The mask is based on historical sea ice extent from 1993-2024." ;
# 		:Conventions = "CF-1.8" ;
# 		:standard_name_vocabulary = "CF Standard Name Table v78" ;
# 		:grid_mapping = "latitude_longitude" ;
# 		:geospatial_lat_min = -89.875 ;
# 		:geospatial_lat_max = 89.875 ;
# 		:geospatial_lon_min = 0.125 ;
# 		:geospatial_lon_max = 359.875 ;
# 		:geospatial_lat_resolution = 0.25 ;
# 		:geospatial_lon_resolution = 0.25 ;
# 		:geospatial_lat_units = "degrees_north" ;
# 		:geospatial_lon_units = "degrees_east" ;
# 		:time_coverage_start = "1993-01-01" ;
# 		:time_coverage_end = "2024-12-31" ;
# 		:creator_name = "NOAA/NCEI" ;
# 		:creator_email = "oisst-team@noaa.gov" ;
# 		:project = "NOAA Optimum Interpolation Sea Surface Temperature (OISST) v3" ;
# 		:processing_level = "L4" ;
# 		:cdm_data_type = "Grid" ;
# }

fn_orig=./oisst_v3_ice_mask_1993-2024.nc
fn_corrected=./oisst_v3_ice_mask_1993-2024_corrected.nc

# Remove flag_values
ncatted -O -h -a flag_values,ice_mask,d,, ${fn_orig} step1.nc

# Remove flag_meanings
ncatted -O -h -a flag_meanings,ice_mask,d,, step1.nc step2.nc

# Change valid min
ncatted -O -h -a valid_min,ice_mask,o,ub,1 step2.nc step3.nc

# Change valid max
ncatted -O -h -a valid_max,ice_mask,o,ub,36 step3.nc step4.nc

# Change description string
new_description="Climatological mask indicating regions capable of sea ice formation. Value of 0 indicates non-ice regions; Values >= 1 indicate ice-capable regions: Values 1-12 are 15-degree bands in the Northern Hemisphere; Value 13 is Baltic Sea; Values 14-16 are not used; Value 17 is south of Asia, west of 75 degrees; Value 18 is south of Asia, between 75 and 90 degrees; Value 19 is south of Asia and North America, between 90 and 130 degrees; Values 20-21 are not used; Value 22 is the Great Lakes; Values 23 and 24 are not used; Values 25-36 are 15 degree bands in the Southern Hemisphere."
ncatted -O -h -a description,ice_mask,o,c,"${new_description}" step4.nc step5.nc

# Convert type for ice_mask from float to ubyte
ncap2 -O -L 9 -s 'ice_mask=ubyte(ice_mask)' step5.nc step6.nc

# Move last step to output file, and clean up
mv step6.nc ${fn_corrected}
rm step?.nc

echo "Original file name:  ${fn_orig}"
echo "Corrected file name: ${fn_corrected}"
