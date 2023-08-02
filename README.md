# ELEVATION API

#### Quick start (docker)

```
    docker-compose up
```

then navigate to:

http://localhost:8080/docs


### Features:

- Handle large amounts of elevation data through geo tiff files
- Interpolate geometries to generate elevation profiles
- Automized coordinate system transformation with provided definitions for many SRID codes

## Setup

### Local setup
Prerequsites:
- GDAL installed and added to path
- Poetry

Create virtual environment and install packages:
```shell
poetry install
```

To get the path to the virtual environemt executable for debugging purposes:

```shell
poetry env info
```

For DEBUGGING run ```debug.py``` file with python interpreter set to **poetry env info** executable path.

Running for production (pyproject.toml script):
```shell
poetry run start
```

### Docker

#### Using docker compose:

```sh
    docker-compose up
```

```/data/*``` directory si setup as mount in the docker image, providing a way to use and manage elevation geo tiff data.

#### Build and run docker image:

```sh
    docker image build .
```
```sh
    docker run hash-of-the-built-image
```



## Configuration 

```./data/config.json```

```json
{
    "datasources": [
        {
            "id": "test1",
            "name": "test1",
            "path": "./lj_eu_dem_v11.tif",
            //"srid": integer (read from geotiff file if not profided, otherwise it will be read from spatial_reference.json),
            //"extent": number[] (array of length 4 representing xmin, ymin, xmax, ymax in the coordinate system srid or )
        }
    ],
    "spatial_ref_sys_path": "./spatial_reference.json"
}
```

Provide all DEM tif files in "datasources" property of config.json.

The provided ```spatial_reference.json``` file defines many coordinate system for any region and is used sometimes if the **.*TIF** file doesnt contain encoded reference system definition.

