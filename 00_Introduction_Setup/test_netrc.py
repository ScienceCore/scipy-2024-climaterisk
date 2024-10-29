# Minimal test to verify NASA Earthdata credentials for downloading data products.
# Requires a .netrc file in home directory containing valid credentials.

import osgeo.gdal, rasterio
from pystac_client import Client
from warnings import filterwarnings
filterwarnings("ignore") # suppress PySTAC warnings

# Mandatory GDAL setup for accessing cloud data
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
osgeo.gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

# Define AOI (Area-Of-Interest) & time-window
livingston_tx, delta = (-95.09, 30.69), 0.1
AOI = tuple(coord + sgn*delta for sgn in (-1,+1) for coord in livingston_tx)
start, stop = '2024-04-30', '2024-05-05'
WINDOW = f'{start}/{stop}'

# Prepare PySTAC client
STAC_URL, COLLECTIONS = 'https://cmr.earthdata.nasa.gov/stac', ["OPERA_L3_DSWX-HLS_V1_1.0"]
catalog = Client.open(f'{STAC_URL}/POCLOUD/')

print("Testing PySTAC search...")
opts = dict(bbox=AOI, collections=COLLECTIONS, datetime=WINDOW)
results = list(catalog.search(**opts).items_as_dicts())
print(len(results))
test_uri = results[0]['assets']['0_B01_WTR']['href']

try:
    print(f"Search successful, accessing test data...")
    with rasterio.open(test_uri) as ds: _ = ds.profile
    print("Success! Your credentials file is correctly configured!")
except:
    print(f"Could not access NASA EarthData asset: {test_uri}")
    print("Ensure that a .netrc file containing valid NASA Earthdata credentials exists in the user home directory.")
