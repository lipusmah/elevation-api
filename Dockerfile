##### DEPENDENCIES
FROM ghcr.io/osgeo/gdal:ubuntu-small-latest as requirements-stage
WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN apt update && apt install -y
RUN apt-get install python3-pip -y

RUN pip install 'poetry==1.5'

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

##### BUILDING
FROM requirements-stage as build-stage

WORKDIR /app

## setup config data volume
RUN mkdir /data
VOLUME /data

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 80
COPY . .
CMD ["uvicorn", "elevation_api.main:app", "--host", "0.0.0.0", "--port", "80", "--root-path", "/"]