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


class NodeType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class NodeMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    color: Optional[tuple[int, int, int, int]] = Field(
        default=pygame.color.THECOLORS["black"])
    max_drones: Optional[int] = Field(ge=1, default=1)
    zone: Optional[NodeType] = Field(default=NodeType.NORMAL)


class Node(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed='allow')

    name: str
    pos: pygame.Vector2
    metadata: Optional[NodeMetadata] = NodeMetadata(
        zone=NodeType.NORMAL)
    connections: Optional[list[Connection]] = []
    cost: Optional[float] = float("inf")
    drones: Optional[dict[int, Drone]] = {}
    edge_case: Optional[dict[int, Drone]] = {}


class Connection(BaseModel):
    from_node: str | Node
    to_node: str | Node
    max_link_capacity: Optional[int] = Field(ge=0, default=1)
    direction: Optional[Direction] = Direction.NONE
    drones: Optional[dict[int, Drone]] = {}


class Config(BaseModel):
    nb_drones: int
    start_node: Node
    end_node: Node
    nodes: dict[str, Node]
    connections: list[Connection]
    drones: list[Drone] | None = None


class Drone(BaseModel):
    id: int
    position: Connection | Node
    next_step: Optional[Connection | Node | None] = None
    on_connection: bool = False
    active: bool = True
    generator: Generator | None = None
    is_waiting: bool = False
