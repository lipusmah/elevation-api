from osgeo import gdal, osr
from osgeo.gdalconst import GA_ReadOnly


def get_extent(tif_path):
    data = gdal.Open(tif_path, GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
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
