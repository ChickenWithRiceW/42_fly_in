from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


# TODO: Will be changed into pygame colors
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    BLACK = "black"
    BROWN = "brown"
    ORANGE = "orange"
    MAROON = "maroon"
    GOLD = "gold"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"
    YELLOW = "yellow"


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class HubMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    color: Optional[Color] = Field(default=Color.GREEN)
    max_drones: Optional[int] = Field(ge=1, default=1)
    zone: Optional[ZoneType] = Field(default=ZoneType.NORMAL)


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    metadata: Optional[HubMetadata] = HubMetadata(
        color=Color.BLUE, zone=ZoneType.NORMAL)
    connections: Optional[list[Connection]] = []


class Connection(BaseModel):
    from_zone: str | Hub
    to_zone: str | Hub
    max_link_capacity: Optional[int] = Field(ge=0, default=1)


class Config(BaseModel):
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    zones: dict[str, Hub]
    connections: list[Connection]
