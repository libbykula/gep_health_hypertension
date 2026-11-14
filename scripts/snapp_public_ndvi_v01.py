# Libby Kula
# 5/28/2026

import numpy as np
import os
import pandas as pd
import geopandas as gpd
import pygeoprocessing as pygeo 
from osgeo import gdal 
import re
import multiprocessing as mp
import time
import rasterio

dir = '/users/3/kula0049/'
base_dir = os.path.join(dir, 'Files/base_data')


# Rasterize 
public_rasterized = os.path.join(base_dir, 'snapp', 'public_lands_only_fixed.tif')

county_boundaries = gpd.read_file(
    os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'metropolitan_counties.gpkg'))


def align_rasters(base_raster, to_align_raster, aligned_output):
    '''Align to_align_raster to match base_raster (extent, resolution, CRS).'''
    with rasterio.open(base_raster) as src:
        bounds = src.bounds
        transform = src.transform
        crs = src.crs
        width = src.width
        height = src.height

    gdal.Warp(
        aligned_output,
        to_align_raster,
        format='GTiff',
        outputBounds=(bounds.left, bounds.bottom, bounds.right, bounds.top),
        width=width,
        height=height,
        dstSRS=crs.to_string(),
        resampleAlg='near'
    )


def rasters_match(r1, r2):
    '''Check if rasters match in shape, transform, and CRS.'''
    with rasterio.open(r1) as src1, rasterio.open(r2) as src2:
        return (
            src1.width == src2.width and
            src1.height == src2.height and
            src1.transform == src2.transform and
            src1.crs == src2.crs
        )
            

def set_to_zero(hm_array, condition_array, public_or_private, nodata):
    # Start with original
    result = hm_array.copy()
    
    # Mask of valid data
    valid_mask = hm_array != nodata

    if public_or_private == 'public':
        result[valid_mask & (condition_array == 0)] = 0
    elif public_or_private == 'private':
        result[valid_mask & (condition_array == 1)] = 0
    else:
        raise ValueError("public_or_private must be 'public' or 'private'")
    return result

def reclassify_raster(c):
    nodata_value = -10

    vector_path = os.path.join(base_dir, 'cartographic', 'cb_2018_us_county_500k', 'indiv', c + '.gpkg')
    vector_gdf = county_boundaries[county_boundaries['GEOID'] == c]
    vector_gdf = vector_gdf.to_crs('EPSG:4326')
    vector_gdf.to_file(vector_path, driver='GPKG')
    
    clipped_public_path = re.sub(r'.tif', r'_clipped_{}.tif'.format(c), public_rasterized)
    gdal.Warp(clipped_public_path, public_rasterized, cutlineDSName=vector_path, cropToCutline=True)
    
    raster_path = os.path.join(base_dir, 'NDVI/ndvi_2019_ave_scaled.tiff')

    aligned_public_path = clipped_public_path.replace('.tif', f'_aligned.tif')
    
    if not rasters_match(raster_path, clipped_public_path):
        print(f'Aligning rasters for {c}')
        align_rasters(raster_path, clipped_public_path, aligned_public_path)
        public_input = aligned_public_path
    else:
        public_input = clipped_public_path
    
    for scen in ['public', 'private']:
        output_path = os.path.join(base_dir, 'NDVI/ndvi_2019_ave_scaled_' + scen + '.tiff')

        # Raster calculator
        pygeo.raster_calculator(
            [(raster_path, 1), (public_input, 1)],
            lambda hm, cond: set_to_zero(hm, cond, scen, nodata_value),
            output_path,
            gdal.GDT_Float32,
            nodata_value
        )