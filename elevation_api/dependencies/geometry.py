from elevation_api.models.geojson import LineString, Polygon, SimpleGeometry
from fastapi import Body
from osgeo import ogr


async def pre_geometry(geometry: SimpleGeometry = Body(), interpolate: None | float = None) -> str:
    json = geometry.json()

    if interpolate is not None:
        g = ogr.CreateGeometryFromJson(json)
        g.Segmentize(interpolate)
        return g.ExportToJson()

    return json


async def pre_ls_poly_geometry(geometry: LineString | Polygon = Body(), interpolate: None | float = None) -> str:
    json = geometry.json()

    if interpolate is not None:
        g = ogr.CreateGeometryFromJson(json)
        g.Segmentize(interpolate)
        return g.ExportToJson()

    return json
