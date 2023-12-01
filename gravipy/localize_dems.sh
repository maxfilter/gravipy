#!/bin/bash

# localizes the MIT Copernicus DEMs (if they don't exist). merges them together. requires wget, gdal

set -e

# DEM filenames
FILE1=Copernicus_DSM_10_N42_00_W072_00
FILE2=Copernicus_DSM_10_N42_00_W071_00

function localize {
     # gets the ellipsoid referenced dem from prism and extract it
     wget https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-30-DGED__2022_1/${1}.tar
     tar -xvf ${1}.tar
     mv ${1}/DEM/${1}_DEM.tif ./
     rm -rf ./${1}
     rm ${1}.tar
}

# localize first DEM if it doesn't exist
if [ ! -f "${FILE1}_DEM.tif" ]; then
    localize ${FILE1}
fi

# localize second DEM if it doesn't exist
if [ ! -f "${FILE2}_DEM.tif" ]; then 
    localize ${FILE2}
fi

# merge tifs together
if [ ! -f "dem.tif" ]; then
    gdal_merge.py -tap -o dem.tif Copernicus_DSM*
fi

