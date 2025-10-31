import os
os.environ['PROJ_LIB'] = 'C:/Users/kibby/miniforge3/pkgs/proj-9.7.0-h9080b7b_0/Library/share/proj'
import pygeoprocessing as pygeo
from osgeo import gdal, gdalconst
import multiprocessing as mp
import re 
import glob

data_dir = 'D:/base_data/GEP/Flood Risk Mitigation/GISA/'
reclassified_dir = 'D:/base_data/GEP/Flood Risk Mitigation/GISA/reclassified/'
resampled_dir = 'D:/base_data/GEP/Flood Risk Mitigation/GISA/resampled/'
os.makedirs(resampled_dir, exist_ok=True)
tif_files = [f for f in os.listdir(data_dir) if f.endswith('.tif')]

wkt_4326 = """GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84", 6378137, 298.257223563,
            LENGTHUNIT["metre", 1]]],
    PRIMEM["Greenwich", 0,
        ANGLEUNIT["degree", 0.0174532925199433]],
    CS[ellipsoidal, 2],
        AXIS["Latitude", north,
            ORDER[1],
            ANGLEUNIT["degree", 0.0174532925199433]],
        AXIS["Longitude", east,
            ORDER[2],
            ANGLEUNIT["degree", 0.0174532925199433]],
    ID["EPSG", 4326]]"""

# for tif in tif_files:
value_map = {i: 1 for i in range(1, 40)}  # 1-39 -> 1
value_map[0] = 0

def compress_tifs(path):
    #Open the input raster
    input_raster_path = path
    output_raster_path = re.sub('.tif', '_compress.tif', path)

    # Open the dataset
    src_ds = gdal.Open(input_raster_path)

    # Define the output options, including compression
    creation_options = ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=IF_SAFER"]

    # Use gdal.Translate to apply the compression
    gdal.Translate(output_raster_path, src_ds, creationOptions=creation_options)

    # Close the dataset
    src_ds = None
    
    os.remove(input_raster_path)

def reclassify_raster(tif):
    input_path = os.path.join(data_dir, tif)
    output_path = os.path.join(reclassified_dir, f"reclass_{tif}")

    # if not os.path.exists(re.sub('.tif', '_compress.tif', output_path)):
    # if not os.path.exists(output_path):
    print(f"Reclassifying {tif}...")
    pygeo.reclassify_raster(
        base_raster_path_band=(input_path, 1),
        value_map=value_map,
        target_raster_path=output_path,
        target_datatype=gdal.GDT_Int32,
        target_nodata=0
    )
        # compress_tifs(output_path)
    # else:
    #     print(f"Skipping {tif} (already reclassified)")    

def replace_nodata_with_zero(tif):
    input_path = os.path.join(reclassified_dir, f"reclass_{tif}")
    output_path = os.path.join(reclassified_dir, f"reclass_2_{tif}")
    
    if os.path.exists(output_path):
        print(f"Skipping {tif} (nodata already replaced)")
        return
    
    print(f"Replacing nodata with zero for {tif}...")

    src_ds = gdal.Open(input_path, gdal.GA_ReadOnly)
    band = src_ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()

    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.CreateCopy(
        output_path, src_ds, strict=0,
        options=[
            "COMPRESS=LZW",
            "TILED=YES",
            "BIGTIFF=YES"
        ]
    )

    # Replace nodata with 0 efficiently using gdal_calc or GDAL API block-by-block
    dst_band = dst_ds.GetRasterBand(1)
    if nodata is not None:
        print(f"Replacing nodata ({nodata}) with 0 in blocks...")
        block_x, block_y = dst_band.GetBlockSize()
        xsize = dst_band.XSize
        ysize = dst_band.YSize
        for y in range(0, ysize, block_y):
            rows = min(block_y, ysize - y)
            for x in range(0, xsize, block_x):
                cols = min(block_x, xsize - x)
                data = dst_band.ReadAsArray(x, y, cols, rows)
                data[data == nodata] = 0
                dst_band.WriteArray(data, x, y)
        dst_band.DeleteNoDataValue()
        dst_band.FlushCache()

    dst_ds = None
    src_ds = None


def resample_raster(tif):
    input_path = os.path.join(reclassified_dir, f"reclass_2_{tif}")
    output_path = os.path.join(resampled_dir, f"resampled_2_{tif}")

    if not os.path.exists(output_path):
        print(f"Resampling {tif}...")
        gdal.Warp(
            destNameOrDestDS=output_path,
            srcDSOrSrcDSTab=input_path,
            xRes=0.002694945852358563636,
            yRes=0.002694945852358563636,
            resampleAlg='average',
            dstSRS=wkt_4326,
            outputType=gdal.GDT_Float32,  # 👈 ensures averages aren’t truncated
            creationOptions=[
                "COMPRESS=LZW",
                "TILED=YES",
                "BIGTIFF=YES"
            ]
        )
    else:
        print(f"Skipping {tif} (already resampled)")


def run_raster(tif):
    # reclassify_raster(tif)
    # try:
    #     replace_nodata_with_zero(tif)
    # except:
    #     print(f"Error replacing nodata with zero for {tif}")
    #     return
    # try:
    #     resample_raster(tif)
    # except:
    #     print(f"Error resampling {tif}")
    #     return

    if not os.path.exists(os.path.join(resampled_dir, f"resampled_2_{tif}")):
        try:
            reclassify_raster(tif)
        except:
            print(f"Error reclassifying {tif}")
            return
        
        try:
            replace_nodata_with_zero(tif)
        except:
            print(f"Error replacing nodata with zero for {tif}")
            return
        
        try:
            resample_raster(tif)
        except:
            print(f"Error resampling {tif}")
            return


# for tif in tif_files:
#     run_raster(tif)
### PARALLEL PROCESSING ####
# if __name__ == '__main__':
#     mp.freeze_support() # This is recommended on Windows
#     # Step 1: Init multiprocessing.Pool()
#     pool = mp.Pool(mp.cpu_count()*2 -2)

#     # Step 2: `pool.map` the `prep_and_run_cooling()` function
#     # pool.map(prep_and_run_cooling_lists, [c for c in metro_list])
#     pool.map(run_raster, [tif for tif in tif_files])

#     # Step 3: Don't forget to close
#     pool.close()    
#     pool.join()

# #### MOSAIC AND COMPRESS RASTER ####O
# resampled_tifs = [f for f in os.listdir(resampled_dir) if f.endswith('.tif')]
resampled_tifs = glob.glob(r"D:/base_data/GEP/Flood Risk Mitigation/GISA/resampled/*.tif")

output_path = os.path.join(data_dir, "GISA_resampled_mosaic.tif")

vrt_path = os.path.join(resampled_dir, "GISA_resampled_mosaic.vrt")
os.makedirs(os.path.dirname(vrt_path), exist_ok=True)

# Build a virtual raster (VRT) to avoid reading all data into memory
gdal.BuildVRT(vrt_path, resampled_tifs)

# Translate the VRT to a compressed GeoTIFF
gdal.Translate(
    output_path,
    vrt_path,
    creationOptions=["COMPRESS=LZW", "TILED=YES", "BIGTIFF=IF_SAFER"]
)

# Clean up VRT
os.remove(vrt_path)

print("Mosaic saved to", output_path)

# compress_tifs(os.path.join(tif_dir, "FloodDepth_RP500_Mosaic.tif"))