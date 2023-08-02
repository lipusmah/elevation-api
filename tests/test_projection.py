from elevation_api.configuration import GeoTiffDatasource
from elevation_api.services.elevations import get_pixel_coordinates

test_tif_1 = GeoTiffDatasource(**{
    "path": "C:\\git\\geo_services\\data\\elevation_api\\./slo_dmv_100m/slo_dmv_100m_3794_g.tif",
    "srid": "3794",
    "proj": "PROJCS[\"Slovenia 1996 / Slovene National Grid\",GEOGCS[\"Slovenia 1996\",DATUM[\"Slovenia_Geodetic_Datum_1996\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],AUTHORITY[\"EPSG\",\"6765\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4765\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",15],PARAMETER[\"scale_factor\",0.9999],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",-5000000],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"3794\"]]",
    "extent": [
        373628.02,
        28484.929999999993,
        625630.900996,
        196482.86023999998
    ],
    "size": [
        2521,
        1680
    ],
    "pixel_size": [
        99.961476,
        -99.998768
    ],
    "name": "slo_dem_100m"

})


def test_2d_index():
    x = 426981.82
    y = 108093.00
    px, py = get_pixel_coordinates(test_tif_1, x, y)
    assert px < test_tif_1.size[0] and py < test_tif_1.size[1], "Value should be smaller than size"


if __name__ == "__main__":
    test_2d_index()
