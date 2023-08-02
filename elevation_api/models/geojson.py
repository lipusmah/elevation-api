from pydantic import BaseModel, Field


class LineString(BaseModel):
    type: str = Field("LineString", const=True)
    coordinates: list


class Point(BaseModel):
    type: str = Field("Point", const=True)
    coordinates: list


class Polygon(BaseModel):
    type: str = Field("Polygon", const=True)
    coordinates: list


class MultiPoint(BaseModel):
    type: str = Field("MultiPoint", const=True)
    coordinates: list


class MultiLineString(BaseModel):
    type: str = Field("MultiLineString", const=True)
    coordinates: list


class MultiPolygon(BaseModel):
    type: str = Field("MultiPolygon", const=True)
    coordinates: list


Geometry = Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon
SimpleGeometry = Point | LineString | Polygon
