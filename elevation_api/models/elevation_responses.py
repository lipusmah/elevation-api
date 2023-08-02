from typing import Union
from elevation_api.configuration import GeoTiffDatasource
from elevation_api.models.geojson import Geometry, LineString, Polygon
from pydantic import BaseModel


class ElevationProfile(BaseModel):
    geometry: LineString | Polygon
    ms: list[float]
    elevations: list[float]
    length: float
    length_3d: float
    proj: str
    srid: int
    min: float
    max: float
    gain: float
    loss: float


class ElevationDetails(BaseModel):
    elevation: float
    datasource: GeoTiffDatasource
    reprojected: tuple[float, float]
    original: tuple[float, float]
    in_proj: str
    in_srid: Union[int, None]
