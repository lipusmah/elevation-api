from elevation_api.dependencies.geometry import pre_geometry, pre_ls_poly_geometry
from elevation_api.dependencies.projection import pre_projection, pre_projections
from elevation_api.models.geojson import Geometry
from elevation_api.services import elevations
from fastapi import APIRouter, Depends
from elevation_api.services.projections import reproject_geometry
from geojson import geometry
from elevation_api.models.elevation_responses import ElevationDetails, ElevationProfile
import json

router = APIRouter()


@router.post("/get_z", response_model=list[float], operation_id="getZList")
async def get_z(geometry: Geometry = Depends(pre_ls_poly_geometry), projection=Depends(pre_projection)) -> list[float]:
    _, proj = projection
    return elevations.get_z_list(geometry, proj)


@router.post("/get_z/details", response_model=list[ElevationDetails], operation_id="getZListDetails")
async def get_z_details(multiple_datasources: bool = False, geometry: Geometry = Depends(pre_ls_poly_geometry), projection=Depends(pre_projection)) -> list[float]:
    srid, proj = projection
    return elevations.get_z_details_list(geometry, proj, srid, multiple_datasources)


@router.post("/get_m", response_model=list[float], operation_id="getMListDetails")
async def get_m(geometry: Geometry = Depends(pre_ls_poly_geometry)) -> list[float]:
    return elevations.get_m_list(geometry)


@router.post("/get_zm", response_model=list[tuple[float, float]], operation_id="getZMList")
async def get_zm(geometry: Geometry = Depends(pre_ls_poly_geometry), projection=Depends(pre_projection)) -> list[float]:
    _, proj = projection
    return elevations.get_zm_list(geometry, proj)


@router.post("/append_z", operation_id="appendZ")
async def append_z(geometry: Geometry = Depends(pre_geometry), projection=Depends(pre_projection)) -> list[float]:
    _, proj = projection
    g = elevations.append_z(geometry, proj)
    return g


@router.post("/profile", response_model=ElevationProfile, operation_id="elevationProfile")
async def reproject(geometry: str = Depends(pre_ls_poly_geometry), projection=Depends(pre_projection)) -> geometry:
    srid, proj = projection
    es = elevations.get_z_list(geometry, proj)
    m, length_3d, gain, loss, min, max, ms = elevations.get_stats(geometry, es)
    profile = ElevationProfile(geometry=json.loads(geometry), length=m, length_3d=length_3d,
                               gain=gain, loss=loss, min=min,  max=max, ms=ms, elevations=es, proj=proj, srid=srid)
    return profile


@router.post("/reproject", response_model=Geometry, operation_id="reproject")
async def reproject(geometry: Geometry = Depends(pre_geometry), projections=Depends(pre_projections)) -> geometry:
    in_proj, out_proj = projections
    return reproject_geometry(geometry, in_proj, out_proj)
