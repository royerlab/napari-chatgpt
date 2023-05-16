import napari

from napari_chatgpt.utils.napari.open_in_napari import open_zarr_in_napari

# url = 'https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr'
# url = 'http://public.czbiohub.org/royerlab/zebrahub/imaging/multi-view/ZMNS001.ome.zarr/'
url = 'https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.1/6001237.zarr'

viewer = napari.Viewer()

z = open_zarr_in_napari(viewer, url)

napari.run()
