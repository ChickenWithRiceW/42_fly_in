from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generator
from enum import Enum, IntEnum
import pygame


class Direction(IntEnum):
    BLOCKED = 0
    BI = 1
    MONO = 2
    NONE = 3


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class HubMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    color: Optional[tuple[int, int, int, int]] = Field(
        default=pygame.color.THECOLORS["black"])
    max_drones: Optional[int] = Field(ge=1, default=1)
    zone: Optional[ZoneType] = Field(default=ZoneType.NORMAL)


class Hub(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed='allow')

    name: str
    pos: pygame.Vector2
    metadata: Optional[HubMetadata] = HubMetadata(
        zone=ZoneType.NORMAL)
    connections: Optional[list[Connection]] = []
    cost: Optional[float] = float("inf")
    drones: Optional[dict[int, Drone]] = {}


class Connection(BaseModel):
    from_zone: str | Hub
    to_zone: str | Hub
    max_link_capacity: Optional[int] = Field(ge=0, default=1)
    direction: Optional[Direction] = Direction.NONE
    drones: Optional[dict[int, Drone]] = {}


class Config(BaseModel):
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    zones: dict[str, Hub]
    connections: list[Connection]
    drones: list[Drone] | None = None


class Drone(BaseModel):
    id: int
    position: Connection | Hub
    next_step: Optional[Connection | Hub | None] = None
    on_connection: bool = False
    active: bool = True
    generator: Generator | None = None
