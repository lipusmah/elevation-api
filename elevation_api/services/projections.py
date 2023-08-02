from elevation_api.models.geojson import Geometry
from osgeo import ogr, osr
import json


def reproject_geometry(geojson_geometry, in_proj: str, out_proj: str) -> Geometry:
    in_sr, out_sr = get_sr(in_proj), get_sr(out_proj)
    geometry = ogr.CreateGeometryFromJson(geojson_geometry)

    geometry.AssignSpatialReference(in_sr)
    geometry.TransformTo(out_sr)

    return json.loads(geometry.ExportToJson())


def create_transformer(in_sr: osr.SpatialReference, out_sr: osr.SpatialReference):
    ct = osr.CreateCoordinateTransformation(in_sr, out_sr)
    return ogr.GeomTransformer(ct)


def reproject_coordinate(x: float, y: float, transformer: ogr.GeomTransformer, in_sr: osr.SpatialReference) -> tuple[float, float]:
    p = create_point(x, y, in_sr)
    o = transformer.Transform(p)
    return [o.GetX(), o.GetY()]


def create_point(x: float, y: float, sr: osr.SpatialReference) -> ogr.Geometry:
    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(x, y)
    p.AssignSpatialReference(sr)
    return p


def get_sr(proj: str):
    sr = osr.SpatialReference()
    sr.ImportFromProj4(proj)
    return sr


def reproject_extent(extent: list[float], proj: str, out_proj: str):
    sr = get_sr(proj)
    out_sr = get_sr(out_proj)
    p1 = create_point(extent[0], extent[1], sr)
    p2 = create_point(extent[2], extent[3], sr)
    p1.TransformTo(out_sr)
    p2.TransformTo(out_sr)
    return [p1.GetX(), p1.GetY(), p2.GetX(), p2.GetY()]
