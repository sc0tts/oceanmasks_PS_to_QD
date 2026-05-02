
README_cdr_vs_qd_masks.txt

The goal here is to compare the ocean masks of the
  NOAA sea ice concentration CDR when those values
  are reprojected from the NSIDC 25km polar stereo
  grids to the quarter-degree lat/lon grid.

The ocean mask for the CDR is taken from the ancillary
  files of version 5 of that product:
    https://nsidc.org/data/g02202/versions/6
  Specifically, the "surface_type" fields of these files:
    https://noaadata.apps.nsidc.org/NOAA/G02202_V6/ancillary/G02202-ancillary-psn25-v06r00.nc
    https://noaadata.apps.nsidc.org/NOAA/G02202_V6/ancillary/G02202-ancillary-pss25-v06r00.nc

The methodology employed here is to:
  Extract an ocean-only mask from these fields (excluding lakes,
    coast, and land from the mask)
  Re-projecting those masks to the quarter-degree lat/lon grid
    using `gdalwarp` and nearest-neighbor interpolation
  Compare these two fields to see where they match up and where they don't.


Location of initial files
-------------------------
To run the processing that allows comparison of the ocean masks,
  Ensure that the CDRv6 ancillary files are in a local subdirectory:
    cdr_ancillary/
    ├── G02202-ancillary-psn25-v06r00.nc
    └── G02202-ancillary-pss25-v06r00.nc

  Also, ensure that the OISST mask is in this directory:
    oisst_orig/
    └── oisst_v3_ice_mask_1993-2024.nc



Correction of OISST mask
------------------------
The OISST as-provided does not plot properly with metadata-aware programs
  such as Panoply because the metadata do not properly describe the 
  data field.

The original metadata for the mask field is:

        float ice_mask(lat, lon) ;
                ice_mask:long_name = "Sea ice capability mask" ;
                ice_mask:units = "1" ;
                ice_mask:valid_min = 0. ;
                ice_mask:valid_max = 1. ;
                ice_mask:flag_values = 0., 1. ;
                ice_mask:flag_meanings = "no_ice_capability ice_capable" ;
                ice_mask:description = "Climatological mask indicating regions capable of sea ice formation. Values >= 0.5 indicate ice-capable regions, < 0.5 indicate non-ice regions." ;

I have created a script -- `rework_oisst_mask.sh` -- that does not
  change the data values (except converting the type from float to ubyte)
  and changes the attributes to better describe the data:

	ubyte ice_mask(lat, lon) ;
                ice_mask:long_name = "Sea ice capability mask" ;
                ice_mask:units = "1" ;
                ice_mask:valid_min = 1UB ;
                ice_mask:valid_max = 36UB ;
                ice_mask:description = "Climatological mask indicating regions capable of sea ice formation. Value of 0 indicates non-ice regions; Values >= 1 indicate ice-capable regions: Values 1-12 are 15-degree bands in the Northern Hemisphere; Value 13 is Baltic Sea; Values 14-16 are not used; Value 17 is south of Asia, west of 75 degrees; Value 18 is south of Asia, between 75 and 90 degrees; Value 19 is south of Asia and North America, between 90 and 130 degrees; Values 20-21 are not used; Value 22 is the Great Lakes; Values 23 and 24 are not used; Values 25-36 are 15 degree bands in the Southern Hemisphere." ;
  

Extract raw binary of mask field
--------------------------------
A utility script -- 'extract_orig_ice_mask.py -- can be used to
  extract a raw binary version of the mask field:

    python extract_orig_ice_mask.py ./oisst_orig/oisst_v3_ice_mask_1993-2024.nc oisst_ice_mask_vals_01-36.dat


Processing to generate ocean-mask comparison fields
---------------------------------------------------

Generate several intermediate versions of the ocean masks with:
  ./process_cdr_watermasks.sh
which executes a variety of gdal commands and python scripts
  and ends with geotiffs of the CDRv6 ocean masks on the
  quarter-degree latlon grid:
    watermask_psn25_on_qd.tif
    watermask_pss25_on_qd.tif
  and creates a geotiff of the water mask from OISST:
    watermask_oisst_on_qd.tif

The script `combine_ocean_masks.py` assumes the above file names
  and formats:
    python combine_ocean_masks.py
  creates
    combined_ocean_masks.dat

I then use ImageJ to read in this 1440x720 uint8 field and apply
  a color table -- combined_water_masks.lut -- to the field and
  save the resulting image as a .gif file:

    combined_ocean_masks.gif 

This allows a comparison of where there is/isn't ocean in the two masks.
  White:  Both CDR and OISST indicate "ocean"
  Black:  Both CDR and OISST indicate "land"
          or OISST indicates not-ocean and the location is off-grid for CDR
   Blue:  Only the CDR mask indicates "ocean"
    Red:  Only the OISST mask indicates "ocean"
