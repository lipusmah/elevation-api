
from elevation_api import main
from elevation_api.models.elevation_responses import ElevationDetails
from elevation_api.models.geojson import Geometry
from elevation_api.services.projections import create_transformer, get_sr, reproject_coordinate
from elevation_api.services.utils import extent_contains, get_distance, get_distance_3d
import struct

from osgeo import gdal, ogr, osr
from elevation_api.configuration import GeoTiffDatasource
import math
import json


def get_pixel_coordinates(tif: GeoTiffDatasource, x: float, y: float) -> tuple[int, int]:
    # top left coordinate as origin
    if tif.pixel_size[1] > 0:
        pix_x = (x - tif.extent[0]) / tif.pixel_size[0]
        pix_y = (y - tif.extent[3]) / tif.pixel_size[1]
        return [math.ceil(pix_x), math.floor(pix_y)]

    pix_x = (x - tif.extent[0]) / tif.pixel_size[0]
    pix_y = (y - tif.extent[3]) / tif.pixel_size[1]
    return [math.floor(pix_x), math.floor(pix_y)]


def read_one_pixel(ds: GeoTiffDatasource, pix_x, pix_y) -> float:
    tif = gdal.Open(ds.path)
    band = tif.GetRasterBand(1)

    scanline = band.ReadRaster(pix_x, pix_y, 1, 1)
    tuple_of_floats = struct.unpack('f' * 1, scanline)

    tif = None
    if len(tuple_of_floats) > 0:
        return tuple_of_floats[0]
    return None


def read_pixels_for_coords(ds: GeoTiffDatasource, pix_coords: list[tuple[int, int]]):
    tif = gdal.Open(ds.path)
    band = tif.GetRasterBand(1)
    es = []
    for px, py in pix_coords:
        scanline = band.ReadRaster(px, py, 1, 1)
        tuple_of_floats = struct.unpack('f' * 1, scanline)

        if len(tuple_of_floats) > 0:
            es.append(tuple_of_floats[0])
        else:
            es.append(None)
    tif = None
    return es


def elevation_at_coordinate(tif: GeoTiffDatasource, x: float, y: float) -> float:
    pix_coords = get_pixel_coordinates(tif, x, y)
    return read_one_pixel(tif, pix_coords[0], pix_coords[1])


def yield_coordinates(geojson: dict):
    geometry = ogr.CreateGeometryFromJson(geojson)
    for i in range(0, geometry.GetPointCount()):
        # GetPoint returns a tuple not a Geometry
        pt = geometry.GetPoint(i)
        yield (pt)


def get_tif_band(tif: GeoTiffDatasource) -> gdal.Band:
    data = gdal.Open(tif.path)
    band = data.GetRasterBand(1)
    return band


def create_transformers(in_sr: osr.SpatialReference) -> dict[str, ogr.GeomTransformer]:
    return {ds.id: create_transformer(in_sr, get_sr(ds.proj)) for ds in main.config.datasources}


def coordinate_in_datasource(x: float, y: float, sr: osr.SpatialReference, multiple_datasets: bool = False):
    for ds in main.config.datasources:
        ds_sr = get_sr(ds.proj)
        xt, yt = reproject_coordinate(x, y, create_transformer(sr, ds_sr), sr)
        if extent_contains(ds.extent, xt, yt):
            yield xt, yt, ds

            if not multiple_datasets:
                break
    return None, None, None


def get_coord_in_datasource(x, y, sr, transformers) -> tuple[float, float, GeoTiffDatasource]:
    for ds in main.config.datasources:
        transformer = transformers[ds.id]
        xt, yt = reproject_coordinate(x, y, transformer, sr)
        if extent_contains(ds.extent, xt, yt):
            return xt, yt, ds
    return None, None, None


def create_elevation_details(x: float, y: float, z: float, xt: float, yt: float, ds: GeoTiffDatasource, proj: str, srid: int) -> ElevationDetails:
    dso = ds.copy()
    dso.path = None
    return ElevationDetails(
        elevation=z,
        datasource=dso,
        reprojected=(xt, yt),
        in_proj=proj,
        in_srid=srid,
        original=(x, y)
    )


def append_datasources(geometry: Geometry, sr, transformers) -> list[tuple[float, float, GeoTiffDatasource]]:
    data: list[tuple[float, float, GeoTiffDatasource]] = []
    for x, y, _ in yield_coordinates(geometry):
        xt, yt, ds = get_coord_in_datasource(x, y, transformers, sr)
        data.append((xt, yt, ds))
    return data


def append_datasources_and_ms(geometry: Geometry, sr, transformers) -> list[tuple[float, float, GeoTiffDatasource]]:
    data: list[tuple[float, float, GeoTiffDatasource]] = []
    ms = []
    m = 0
    prev = None
    for i, (x, y, _) in enumerate(yield_coordinates(geometry)):
        if i == 0:
            prev = (x, y)
            ms.append(m)
        else:
            m += get_distance(prev, (x, y))
            ms.append(m)
        prev = (x, y)
        xt, yt, ds = get_coord_in_datasource(x, y, transformers, sr)
        data.append((xt, yt, ds))

    return data, ms


def append_datasources_and_original(geometry: Geometry, sr, transformers) -> list[tuple[float, float, float, float, GeoTiffDatasource]]:
    data: list[tuple[float, float, GeoTiffDatasource]] = []
    for x, y, _ in yield_coordinates(geometry):
        xt, yt, ds = get_coord_in_datasource(x, y, transformers, sr)
        data.append((x, y, xt, yt, ds))
    return data


def get_z_list(geometry: Geometry, proj: str) -> list[float]:
    sr = get_sr(proj)
    transformers = create_transformers(sr)

    coords_with_datasource = append_datasources(geometry, transformers, sr)
    grouped, used_datasources = group_by_datasource(coords_with_datasource)
    elevs = get_elevations_for_datasources(grouped, used_datasources)

    return elevs


def get_z_details_list(geometry: Geometry, proj: str) -> list[ElevationDetails]:
    sr = get_sr(proj)
    transformers = create_transformers(sr)

    coords_with_datasource = append_datasources(geometry, transformers, sr)
    grouped, used_datasources = group_by_datasource(coords_with_datasource)
    elevs = get_elevations_for_datasources(grouped, used_datasources)
    out = []
    for i, (x, y, xt, yt, ds) in coords_with_datasource:
        elev = elevs[i]
        out.append(create_elevation_details(x, y, xt, yt, ds, elev))

    return out


def get_m_list(geometry: Geometry):
    ms = []
    m = 0
    prev = None
    for i, (x, y, _) in enumerate(yield_coordinates(geometry)):
        if i == 0:
            ms.append(0)
        else:
            m += get_distance(prev, (x, y))
            ms.append(m)
        prev = (x, y)

    return ms


def get_stats(geometry: Geometry, elevations: list[float]):
    length_3d = 0
    gain, loss = 0, 0
    ms = []
    min, max = 999999, -999999
    m = 0
    prev = None
    prev_elevation = None
    for i, (x, y, _) in enumerate(yield_coordinates(geometry)):
        e = elevations[i]
        if i == 0:
            ms.append(0)
        else:
            m += get_distance(prev, (x, y))
            length_3d += get_distance_3d((prev[0],
                                         prev[1], prev_elevation), (x, y, e))
            ms.append(m)
            if prev_elevation < e:
                gain += e - prev_elevation
            else:
                loss += prev_elevation - e
            if e < min:
                min = e
            if e > max:
                max = e

        prev_elevation = e
        prev = (x, y)

    return m, length_3d, gain, loss, min, max, ms


def get_zm_list(geometry: Geometry, proj: str) -> list[tuple[float, float]]:
    sr = get_sr(proj)
    transformers = create_transformers(sr)

    coords_with_datasource, ms = append_datasources_and_ms(
        geometry, transformers, sr)
    grouped, used_datasources = group_by_datasource(coords_with_datasource)
    elevs = get_elevations_for_datasources(grouped, used_datasources)

    return tuple(zip(elevs, ms))


def get_elevations_for_datasources(grouped: dict[str, dict[int, list[tuple[float, float]]]], datasources) -> list[float]:
    data = []
    for dsid in grouped:
        ds = datasources[dsid]
        ranges = grouped[dsid]
        for rang in ranges:
            coords = ranges[rang]
            pix_coords = [get_pixel_coordinates(ds, x, y) for x, y in coords]
            eles = read_pixels_for_coords(ds, pix_coords)
            data.append((rang, eles))

    data.sort(key=lambda i: i[0])
    # removing tuple and flattening coordinates for output
    return [i for es in [i[1] for i in data] for i in es]


def group_by_datasource(data: list[tuple[float, float, GeoTiffDatasource]]):
    grouped: dict[str, dict[int, list[tuple[float, float]]]] = {}
    last_ds = None
    datasources = {}
    c = 0

    for xt, yt, ds in data:
        if ds.id not in grouped:
            grouped[ds.id] = {}
            datasources[ds.id] = ds
        if last_ds is not None and last_ds == ds.id:
            last_ds = ds.id
            grouped[ds.id][c].append((xt, yt))
        else:
            c += 1
            last_ds = ds.id
            grouped[ds.id][c] = [(xt, yt)]

    return grouped, datasources


def append_z(geojson: Geometry, proj) -> Geometry:
    geometry = ogr.CreateGeometryFromJson(geojson)
    zs = get_z_list(geojson, proj)
    for i in range(0, geometry.GetPointCount()):
        # GetPoint returns a tuple not a Geometry
        z = zs[i]
        x, y, _ = geometry.GetPoint(i)
        geometry.SetPoint(i, x, y, z)
    return json.loads(geometry.ExportToJson())
