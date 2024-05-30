from osgeo import gdal, osr
from osgeo.gdalconst import GA_ReadOnly


def get_extent(tif_path):
    # Open the dataset
    data = gdal.Open(tif_path, gdal.GA_ReadOnly)
    
    if data is None:
        raise FileNotFoundError(f"Unable to open {tif_path}")
    
    geoTransform = data.GetGeoTransform()
    
    # Get the raster size
    cols = data.RasterXSize
    rows = data.RasterYSize
    
    # Calculate the extent coordinates
    def transform(x, y, gt):
        """Transform pixel coordinates to geospatial coordinates."""
        xp = gt[0] + x * gt[1] + y * gt[2]
        yp = gt[3] + x * gt[4] + y * gt[5]
        return xp, yp

    corners = [
        transform(0, 0, geoTransform),        # Top-left
        transform(cols, 0, geoTransform),     # Top-right
        transform(cols, rows, geoTransform),  # Bottom-right
        transform(0, rows, geoTransform)      # Bottom-left
    ]
    
    # Initialize min and max values
    minx = min(corners, key=lambda c: c[0])[0]
    maxx = max(corners, key=lambda c: c[0])[0]
    miny = min(corners, key=lambda c: c[1])[0]
    maxy = max(corners, key=lambda c: c[1])[0]

    data = None
    return [minx, miny, maxx, maxy]

def get_srid(tif_path):
    data = gdal.Open(tif_path)
    proj = osr.SpatialReference(data.GetProjection())
    data = None
    return proj.GetAttrValue('AUTHORITY', 1)


def get_size(tif_path):
    data = gdal.Open(tif_path)
    return [data.RasterXSize, data.RasterYSize]


def get_pixel_size(tif_path):
    data = gdal.Open(tif_path)
    geoTransform = data.GetGeoTransform()
    return [geoTransform[1], geoTransform[5]]


def get_proj(tif_path):
    data = gdal.Open(tif_path)
    proj = data.GetProjection()
    data = None
    return proj


if __name__ == "__main__":
    t_file = "C:\git\elevation-api\data\datasources\eu_dem_v11_E40N20\eu_dem_v11_E40N20.TIF"
    print(get_extent(t_file))
    print(get_srid(t_file))
    print(get_proj(t_file))
