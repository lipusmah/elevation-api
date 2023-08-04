from elevation_api.configuration import GeoTiffDatasource, Projection
from elevation_api.dependencies.projection import pre_projection
from elevation_api.services.projections import reproject_extent
from fastapi import APIRouter, Depends, HTTPException
from elevation_api import main

router = APIRouter()


@router.get("/datasources", response_model=list[GeoTiffDatasource])
async def datasources(projection=Depends(pre_projection)):
    srid, proj = projection
    dss = main.config.datasources.copy()
    for ds in dss:
        ds.extent = reproject_extent(ds.extent, ds.proj, proj)
        ds.path = None
    return main.config.datasources


@router.get("/srs/{srid}", response_model=Projection)
async def spatial_refs(srid: int) -> Projection:
    if srid in main.config.spatial_ref_sys.projections:
        response = main.config.spatial_ref_sys.projections[srid]
        return response
    raise HTTPException(status_code=404, detail="Spatial reference not found")