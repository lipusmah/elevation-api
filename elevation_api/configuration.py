from typing import Union
from elevation_api.services.utils import get_random_string, read_file_as_json
from .services.geotiff_utils import get_srid, get_extent, get_proj, get_size, get_pixel_size
import os
from pydantic import BaseModel


class Projection(BaseModel):
    srid: int
    auth_name: str
    auth_srid: int
    srtext: str
    proj4text: str


class ProjectionsConfig(BaseModel):
    projections: dict[int, Projection] = {}


class Extent(BaseModel):
    minx: float
    miny: float
    maxx: float
    maxy: float


class GeoTiffDatasource(BaseModel):
    id: str
    path: str = None
    srid: int
    proj: str
    extent: list[float]
    size: list[float, float]
    pixel_size: list[float, float]
    name: str


class ElevationApiConfig(BaseModel):
    epsg: str = "4326"
    datasources: list[GeoTiffDatasource] = []
    spatial_ref_sys: ProjectionsConfig
    source: dict
    path: str


def create_projection_config(config_json: list[dict]):
    return {p["srid"]: Projection(**p) for p in config_json}


def create_geotiff_datasource(conf: dict, base_path: str) -> GeoTiffDatasource:
    path = try_get_full_path(conf["path"], base_path)
    data = {}
    data["id"] = conf["id"] if "id" in conf else get_random_string()
    data["path"] = path
    data["name"] = conf["name"]
    data["size"] = get_size(path)
    data["pixel_size"] = get_pixel_size(path)
    data["srid"] = conf["srid"] if "srid" in conf.keys(
    ) else get_srid(path)

    data["extent"] = conf["extent"] if "extent" in conf.keys(
    ) else get_extent(path)

    data["proj"] = conf["proj"] if "proj" in conf.keys(
    ) else get_proj(path)

    return GeoTiffDatasource(**data)


def contains(extent: BaseModel, x: float, y: float):
    return extent.minx < x < extent.maxx and extent.miny < y < extent.maxy


def try_get_full_path(path, base_path=None):
    if os.path.isfile(path):
        return path
    elif base_path is not None and os.path.isfile(os.path.join(base_path, path)):
        return os.path.join(base_path, path)
    else:
        raise FileNotFoundError(f'path: {path}, base: {base_path}')


class ElevationApiConfig():
    epsg: str = "3857"
    datasources: list[GeoTiffDatasource] = []
    spatial_ref_sys: ProjectionsConfig
    source: dict
    path: str

    def __init__(self, config_path: str = None):
        self.path = os.path.dirname(config_path)
        if config_path is not None:
            self.source = read_file_as_json(config_path)
            self.setup_datasources(self.source)
            self.setup_srids(self.source)

    def get_datasource(self,datasource_id: str):
        for ds in self.datasources:
            if ds.id == datasource_id:
                return ds

    def setup_datasources(self, config_json: dict):
        self.datasources = [create_geotiff_datasource(
            tiff, self.path) for tiff in config_json['datasources']]

    def setup_srids(self, config_json: dict):
        path = try_get_full_path(
            config_json["spatial_ref_sys_path"], self.path)
        conf = read_file_as_json(path)
        conf = {item["srid"]: item for item in conf}
        self.spatial_ref_sys = ProjectionsConfig(**{"projections": conf})
