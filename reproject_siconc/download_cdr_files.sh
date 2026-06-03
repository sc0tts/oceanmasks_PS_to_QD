#!/bin/bash
#
# download_cdr_files.sh
#

src=scotts@nusnow.colorado.edu
nh_file=/projects/DATASETS/NOAA/G02202_V6/north/daily/2026/sic_psn25_20260501_am2_v06r00.nc
sh_file=/projects/DATASETS/NOAA/G02202_V6/south/daily/2026/sic_pss25_20260501_am2_v06r00.nc

scp ${src}:${nh_file} ./
scp ${src}:${sh_file} ./
