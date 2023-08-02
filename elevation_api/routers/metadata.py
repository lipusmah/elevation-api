from elevation_api.configuration import GeoTiffDatasource, Projection
from elevation_api.dependencies.projection import pre_projection
from elevation_api.services.projections import reproject_extent
from fastapi import APIRouter, Depends
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


@router.get("/srs", response_model=list[Projection])
async def spatial_refs() -> dict[int, Projection]:
    response = [main.config.spatial_ref_sys[i]
                for i in main.config.spatial_ref_sys]
    return response
