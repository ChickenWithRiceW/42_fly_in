from dataclasses import dataclass
from pygame import Vector2


@dataclass
class Pos_values:
    min_val: Vector2
    max_val: Vector2
    difference: Vector2


@dataclass
class Scale:
    pos: Vector2
    full_scale: int
