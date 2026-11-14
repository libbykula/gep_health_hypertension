# Libby Kula
#  Global GEP Hypertension
# 11/6/2025
# Update: Converting OR to RR using prevalence as baseline risk and using the mental health team's PC 
# Taking out the things that can be done once for each country rather than each smod_id 

import os
import numpy as np
import rioxarray as rxr
import geopandas as gpd
import pandas as pd
import pygeoprocessing as pygeo
import pygeoprocessing.kernels
from osgeo import gdal
import re
import xarray as xr
from osgeo import osr

# set wd
dir = '/users/3/kula0049/'
base_dir = os.path.join(dir, 'Files/base_data')

urban_boundaries = gpd.read_file(
    os.path.join(dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg/urbanspatial-guppd-v1-gpkg.gpkg'),
    layer='urbanspatial_guppd_v1_polygons'
)

# Save results to CSV
output_dir = os.path.join(dir, 'gep_health/output/linear_11_17_25_v02')
ndvi_path = os.path.join(base_dir, 'NDVI/ndvi_2019_ave_scaled.tiff')  #  annual?

os.makedirs(output_dir, exist_ok=True)

def get_hypertension_gep(c, price_dc_pp, country_label, perc_adults, country_prev):
    # Load data

    vector_path = os.path.join(dir, 'urban-cooling/Data/urbanspatial-guppd-v1-gpkg/indiv/' + c + '.gpkg')
    
    if os.path.exists(vector_path):
        vector_gdf = gpd.read_file(vector_path)
    else:
        vector_gdf = urban_boundaries[urban_boundaries['SMOD_ID'] == c]
        vector_gdf.to_file(vector_path, driver='GPKG')

    country = vector_gdf['CNTRY_NAME'].values[0]
    
    ### Preparing Rasters #########################################################################
    pop_path = os.path.join(base_dir, 'Population/worldpop_2019/' + country_label + '_pop_2019_CN_100m_R2025A_v1.tif')

    # print(f'Pixel size: {pixel_width} x {pixel_height} degrees')
    # for path in [pop_path, ndvi_path]:
    #     gdal.Warp(re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), path),  # How do I keep the buffer on the NDVI though?
    #                         path, cutlineDSName=vector_path, cropToCutline=True)
    #     # gdal.Warp(re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), path), 
    #     #             re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), path), dstSRS='EPSG:4326')

    # data = gdal.Open(re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), pop_path))
    # # data = gdal.Open(re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), ndvi_path))
    # gt = data.GetGeoTransform()
    # pixel_width = gt[1]
    # pixel_height = abs(gt[5])  # usually negative, so take abs

    # pygeo.align_and_resize_raster_stack(base_raster_path_list = [re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), pop_path), 
    #                                                             re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), ndvi_path)],
    #                                     target_raster_path_list = [re.sub(r'\.(.*?)$', r'_al_{}.\1'.format(c), pop_path), 
    #                                                             re.sub(r'\.(.*?)$', r'_al_{}.\1'.format(c), ndvi_path)],
    #                                     resample_method_list = ['bilinear', 'bilinear'],
    #                                     target_pixel_size = [pixel_width, pixel_height],
    #                                     bounding_box_mode = 'union')

    # # Use pygeo dichotomous distance
    kernel_path = os.path.join(base_dir, 'kernels/kernel_500m.tif')

    # if not os.path.exists(kernel_path):
    #     pygeoprocessing.kernels.dichotomous_kernel(target_kernel_path = kernel_path,
    #             max_distance = 5,
    #             normalize=True) # 500 m, pixel size is 100m and max_distance is in pixels 

    ndvi_aligned_path = re.sub(r'\.(.*?)$', r'_al_{}.\1'.format(c), ndvi_path)

    mean_ndvi_500m_path = os.path.join(base_dir, 'NDVI/mean_ndvi_500m_' + c + '.tif')

    # pygeo.convolve_2d(
    #     signal_path_band=(ndvi_aligned_path, 1),  # (raster path, band number)
    #     kernel_path_band=(kernel_path, 1),
    #     target_path=mean_ndvi_500m_path,
    #     normalize_kernel=True  # ensures you get a mean, not a sum
    # )

    ### Preparing prevalence, price, and OR #########################################################################

    # Price
    or_500m = 0.945 # halfway between Bu and Zhang 

    ### Computing avoided cases and costs #########################################################################
    def compute_avoided_cases_from_scalar_prevalence(ndvi_path, pop_path, observed_prevalence, or_per_0_1):
        '''
        Compute avoided hypertension cases due to greenness, assuming a uniform observed prevalence
        and counterfactual of NDVI = 0.

        Parameters:
            ndvi_path (str): Path to NDVI raster (0–1 values).
            pop_path (str): Path to population raster (counts per pixel).
            observed_prevalence (float): Scalar prevalence at current NDVI (e.g., 0.25 for 25%).
            or_per_0_1 (float): Odds ratio per 0.1 NDVI increment (e.g., 0.90).

        Returns:
            avoided_cases (xr.DataArray): Raster of avoided hypertension cases per pixel.
            total_avoided (float): Total avoided cases summed over all pixels.
            baseline_prevalence (xr.DataArray): Raster of estimated prevalence if NDVI = 0.
        '''
        # Load rasters
        ndvi = rxr.open_rasterio(ndvi_path, masked=True).squeeze()
        pop = rxr.open_rasterio(pop_path, masked=True).squeeze()

        # Align rasters
        ndvi, pop = xr.align(ndvi, pop)

        # Valid data mask
        valid_mask = (
            ndvi.notnull() & pop.notnull() &
            (pop > 0) & (observed_prevalence > 0) & (observed_prevalence < 1)
        )

        # Total population
        total_population = pop.where(valid_mask).sum().item()

        # NDVI in 0.1 unit increments
        increments = ndvi.where(valid_mask) / 0.1

        ## Following mental health team's approach 
        # Convert OR to RR using baseline risk (observed prevalence)
        rr_per_0_1 = or_per_0_1 / (1 - observed_prevalence + (observed_prevalence * or_per_0_1))
        # rr = np.exp(np.log(rr_per_0_1) * increments)

        # Estimating preventable cases using RR
        q_j = observed_prevalence * increments * (1-rr_per_0_1) * pop.where(valid_mask) * perc_adults

        # Avoided cases = pop × (baseline - observed)
        avoided_cases = q_j
        avoided_cases = avoided_cases.where(valid_mask)

        # Total avoided cases
        total_avoided = avoided_cases.sum().item()

        return avoided_cases, total_avoided, total_population

    avoided, total, total_pop = compute_avoided_cases_from_scalar_prevalence(
        ndvi_path=mean_ndvi_500m_path,
        pop_path=re.sub(r'\.(.*?)$', r'_al_{}.\1'.format(c), pop_path),
        observed_prevalence=country_prev / 100,  
        or_per_0_1=or_500m
    )

    # print(f'Total avoided cases, linear: {total:,.0f}')
    # print(f'Avoided cases as percent of population, linear: {total/total_pop:.2%}')
    # print(f'Total value of avoided hypertension cases, linear: ${total*price_dc_pp:,.0f}')
    
    out_df = pd.DataFrame({
        'SMOD_ID': [c],
        'country': [country],
        'total_avoided_cases': [total],
        'total_population': [total_pop],
        'avoided_percent_pop': [total / total_pop if total_pop != 0 else 0],
        'total_value_usd': [total * price_dc_pp],
        'price_dc_pp': [price_dc_pp],
        'country_prev': [country_prev]
    })
    # Optional: save rasters
    # avoided.rio.to_raster('Data/avoided_hypertension_cases.tif')
    out_path = os.path.join(output_dir, f'{c}_hypertension_results_2019_linear.csv')
    out_df.to_csv(out_path, index=False)
    print(f'Saved results to {out_path}')

    ### Deleting unnecessary files 
    delete_files = [re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), pop_path),
                    re.sub(r'\.(.*?)$', r'_cropped_{}.\1'.format(c), ndvi_path),
                    re.sub(r'\.(.*?)$', r'_al_{}.\1'.format(c), pop_path),
                    vector_path,
                    mean_ndvi_500m_path,
                    ndvi_aligned_path]
    for file in delete_files:
        if os.path.exists(file):
            os.remove(file)