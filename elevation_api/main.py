from fastapi import FastAPI
import uvicorn
from elevation_api import configuration
from elevation_api.routers import elevation, metadata, geometry
from fastapi_cprofile.profiler import CProfileMiddleware
import os

app = FastAPI()

config_path = os.getenv("ELEVATIONAPI_CONFIG_PATH")

# debug: endpoint profiler
# app.add_middleware(CProfileMiddleware, enable=True, server_app=app,
#                    print_each_request=True, filename="output.txt", strip_dirs=False, sort_by='cumulative')

# todo: handle development environment (docker default: "./data/config.json")
# config = configuration.ElevationApiConfig(
#     "C:\git\geo_services\data\elevation_api\config.json")

# def list_files(startpath):
#     for root, dirs, files in os.walk(startpath):
#         level = root.replace(startpath, '').c ount(os.sep)
#         indent = ' ' * 4 * (level)
#         print('{}{}/'.format(indent, os.path.basename(root)))
#         subindent = ' ' * 4 * (level + 1)
#         for f in files:
#             print('{}{}'.format(subindent, f))
# list_files("../.")

if config_path is None:
    config_path = "/data/config.json"

config = configuration.ElevationApiConfig(config_path)

app.include_router(geometry.router, prefix="/geometry",
                   tags=["Geometry"])
app.include_router(elevation.router, prefix="/elevation",
                   tags=["Elevation"])
app.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])


def start():
    uvicorn.run("elevation_api.main:app",
                host="127.0.0.1", port=8000, reload=True)
