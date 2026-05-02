#!/bin/bash
#
# remove_intermediate_files.sh
# 
# Remove files created by processing, but not considered "final"
rm -v combined_ocean_masks.dat
rm -v landmask_psn25.dat
rm -v landmask_pss25.dat
rm -v oisst_land.dat
rm -v oisst_water.dat
rm -v rawmask_psn25.dat
rm -v rawmask_pss25.dat
rm -v watermask_psn25.dat
rm -v watermask_psn25.tif
rm -v watermask_pss25.dat
rm -v watermask_pss25.tif
