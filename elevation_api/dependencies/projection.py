from elevation_api import main

ProjsInfo = tuple[str, str]
ProjInfo = tuple[int | None, str]


async def pre_projection(srid: int = 3857, proj: str | None = None) -> ProjInfo:
    if proj is not None:
        return [srid, proj]
    else:
        return [srid, main.config.spatial_ref_sys.projections[srid].proj4text]


async def pre_projections(in_srid: int = 3857, out_srid: int = 3857, in_proj: str | None = None, out_proj: str | None = None) -> ProjsInfo:
    if in_proj is None:
        in_proj = main.config.spatial_ref_sys.projections[in_srid].proj4text
    if out_proj is None:
        out_proj = main.config.spatial_ref_sys.projections[out_srid].proj4text
    return in_proj, out_proj
