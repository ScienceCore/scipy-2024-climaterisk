# Helper methods for case study notebooks
import numpy as np
import rasterio
import xarray as xr
import pandas as pd

def search_to_df(results, layer_name):
        '''
        method that takes in search results from a PySTAC Earthdata query and loads the data into a pandas dataframe
        the data frame has columns of date of acquisition, data URLs, and tile ID
        '''

        times = pd.DatetimeIndex([result['properties']['datetime'] for result in results]) # parse of timestamp for each result
        data = {'hrefs': [value['href'] for result in results for key, value in result['assets'].items() if layer_name in key],  # parse out links only to DIST-STATUS data layer
                'tile_id': [value['href'].split('/')[-1].split('_')[3] for result in results for key, value in result['assets'].items() if layer_name in key]}

        # Construct pandas dataframe to summarize granules from search results
        granules = pd.DataFrame(index=times, data=data)
        granules.index.name = 'times'

        return granules

def filter_search_by_cc(results, cloud_threshold=10):
    '''
    Given a list of results returned by the NASA Earthdata STAC API for OPERA DSWx data,
    filter them by cloud cover

    The DSWx data does not always have cloud cover in the metadata. When this is the case,
    read the image and calculate the cloud fraction and apply the threshold
    '''

    filtered_results = []

    for result in results:
        try:
            cloud_cover = result['properties']['eo:cloud_cover']
        except:
            href = result['assets']['0_B01_WTR']['href']
            with rasterio.open(href) as ds:
                img = ds.read(1).flatten()
                cloud_cover = 100*(np.sum(np.isin(img, 253))/img.size)

        if  cloud_cover <= cloud_threshold:
            filtered_results.append(result)

    return filtered_results


def urls_to_dataset(granule_dataframe):
    '''method that takes in a list of OPERA tile URLs and returns an xarray dataset with dimensions
    latitude, longitude and time'''

    dataset_list = []
    
    for i, row in granule_dataframe.iterrows():
        with rasterio.open(row.hrefs) as ds:
            # extract CRS string
            crs = str(ds.crs).split(':')[-1]

            # extract the image spatial extent (xmin, ymin, xmax, ymax)
            xmin, ymin, xmax, ymax = ds.bounds

            # the x and y resolution of the image is available in image metadata
            x_res = np.abs(ds.transform[0])
            y_res = np.abs(ds.transform[4])

            # read the data 
            img = ds.read()

            # Ensure img has three dimensions (bands, y, x)
            if img.ndim == 2:
                img = np.expand_dims(img, axis=0) 

        lon = np.arange(xmin, xmax, x_res)
        lat = np.arange(ymax, ymin, -y_res)

        lon_grid, lat_grid = np.meshgrid(lon, lat)

        da = xr.DataArray(
            data=img,
            dims=["band", "y", "x"],
            coords=dict(
                lon=(["y", "x"], lon_grid),
                lat=(["y", "x"], lat_grid),
                time=i,
                band=np.arange(img.shape[0])
            ),
            attrs=dict(
                description="OPERA DIST data",
                units=None,
            ),
        )
        da.rio.write_crs(crs, inplace=True)

        dataset_list.append(da)
    return xr.concat(dataset_list, dim='time').squeeze()