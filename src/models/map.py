from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Generator
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
    color: tuple[int, int, int, int] = Field(
        default=pygame.color.THECOLORS["black"])
    max_drones: int = Field(ge=1, default=1)
    zone: NodeType = Field(default=NodeType.NORMAL)


class Node(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    pos: pygame.Vector2
    metadata: NodeMetadata = NodeMetadata(
        zone=NodeType.NORMAL)
    connections: list[Connection] = []
    cost: float = float("inf")
    drones: dict[int, Drone] = {}


class Connection(BaseModel):
    model_config = ConfigDict(extra='forbid')

    from_node: Node
    to_node: Node
    max_link_capacity: int = Field(ge=1, default=1)
    direction: Direction = Direction.NONE
    drones: dict[int, Drone] = {}


class Config(BaseModel):
    nb_drones: int
    start_node: Node
    end_node: Node
    nodes: dict[str, Node]
    connections: list[Connection]
    drones: list[Drone] = []


class Drone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    position: Connection | Node
    next_step: Node | Connection
    on_connection: bool = False
    active: bool = True
    generator: Generator[pygame.Vector2, None, None] | None = None
    is_waiting: bool = False
