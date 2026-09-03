from dataclasses import dataclass
from typing import Generator
from pygame import Vector2


@dataclass
class Drone:
    id: int
    pos: Vector2
    animation: None | Generator = None


@dataclass
class Pos_values:
    min_val: Vector2
    max_val: Vector2
    difference: Vector2


@dataclass
class Scale:
    pos: Vector2
    full_scale: int
