from elevation_api.dependencies.projection import pre_projection
from elevation_api.services.geotiff_utils import get_srid
from elevation_api.services.projections import get_sr
from fastapi import APIRouter, Depends, Response
from elevation_api.services import elevations

from elevation_api.models.elevation_responses import ElevationDetails
router = APIRouter()


@router.get("/{x}/{y}", response_model=float | None, operation_id="getElevation")
async def elevation(x: float, y: float, projection=Depends(pre_projection)) -> float:
    _, proj = projection
    sr = get_sr(proj)
    
    try:
        xt, yt, ds = next(elevations.coordinate_in_datasource(x, y, sr))
        return elevations.elevation_at_coordinate(ds, xt, yt)
    
    except StopIteration as e:
        return None


@ router.get("/{x}/{y}/details", response_model=ElevationDetails | None, operation_id="getElevationDetails")
async def elevation_details(x: float, y: float, projection=Depends(pre_projection)) -> float:
    srid, proj = projection
    sr = get_sr(proj)
    
    try:
        xt, yt, ds = next(elevations.coordinate_in_datasource(x, y, sr))
        elevation = elevations.elevation_at_coordinate(ds, xt, yt)
        return elevations.create_elevation_details(x, y, elevation, xt, yt, ds, proj, srid)

    except StopIteration as e:
        return None
