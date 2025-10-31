import ee
import time

# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='global-gross-ecosystem-product')

# -------------------------------
# USER SETTINGS
# -------------------------------
AOI_ASSET = 'projects/global-gross-ecosystem-product/assets/urbanspatial-guppd-v1'
EXPORT_FOLDER = 'GEE_exports'
YEAR = 2019
BATCH_SIZE = 1000          # number of AOIs per batch
SLEEP_TIME = 60          # seconds to wait between batch checks
SCALE = 30

# -------------------------------
# FUNCTIONS
# -------------------------------
def apply_scale_factors(image):
    optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)

def mask_l457(image):
    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(int('11111',2)).eq(0)
    return image.updateMask(mask)

def mask_l8(image):
    qa = image.select('QA_PIXEL')
    sat = image.select('QA_RADSAT').eq(0)
    mask = qa.bitwiseAnd(int('11111',2)).eq(0)
    return image.updateMask(mask).updateMask(sat)

def add_ndvi_l57(image):
    return image.addBands(image.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI'))

def add_ndvi_l8(image):
    return image.addBands(image.normalizedDifference(['SR_B5','SR_B4']).rename('NDVI'))

def get_ndvi_collection(start_date, end_date):
    L5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterDate(start_date, end_date).map(apply_scale_factors).map(mask_l457).map(add_ndvi_l57)
    L7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterDate(start_date, end_date).map(apply_scale_factors).map(mask_l457).map(add_ndvi_l57)
    L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(start_date, end_date).map(apply_scale_factors).map(mask_l8).map(add_ndvi_l8)
    ndvi_all = L5.merge(L7).merge(L8).select('NDVI')
    ndvi_median = ndvi_all.median()
    return ndvi_median

def submit_task(feature, ndvi_image):
    smod_id = feature.get('SMOD_ID').getInfo()
    geom = feature.geometry()
    description = f'NDVI_{smod_id}_{YEAR}'
    filename = f'NDVI_{smod_id}_{YEAR}'
    task = ee.batch.Export.image.toDrive(
        image=ndvi_image.clip(geom),
        description=description,
        folder=EXPORT_FOLDER,
        fileNamePrefix=filename,
        region=geom,
        scale=SCALE,
        maxPixels=1e13,
        fileFormat='GeoTIFF',
        formatOptions={'cloudOptimized': True}
    )
    task.start()
    return task

# -------------------------------
# MAIN SCRIPT
# -------------------------------
# Load AOIs
urbans = ee.FeatureCollection(AOI_ASSET)
size = urbans.size().getInfo()
print(f"Total AOIs: {size}")

# Prepare NDVI
start_date = f'{YEAR}-01-01'
end_date = f'{YEAR}-12-31'
ndvi_median = get_ndvi_collection(start_date, end_date)

# Split AOIs into batches
urbans_list = urbans.toList(size)
tasks = []

for i in range(0, size, BATCH_SIZE):
    batch = urbans_list.slice(i, i + BATCH_SIZE)
    print(f"Submitting batch {i//BATCH_SIZE + 1} ({i} to {min(i+BATCH_SIZE, size)})")
    for j in range(batch.size().getInfo()):
        feature = ee.Feature(batch.get(j))
        task = submit_task(feature, ndvi_median)
        tasks.append(task)
    
    # Wait until tasks are no longer "READY" or "RUNNING" beyond concurrency limit
    while True:
        running = [t.status()['state'] for t in tasks if t.status()['state'] in ['READY', 'RUNNING']]
        print(f"Currently running/queued tasks: {len(running)}")
        if len(running) < 400:  # EE allows ~400 concurrent tasks
            break
        time.sleep(SLEEP_TIME)

print("All batches submitted!")
