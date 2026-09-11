from src.models import NodeType, Node, Connection
import pygame
from pygame import Vector2
from typing import Generator


class RenderHelper:
    @staticmethod
    def get_zone_type_color(zone_type: NodeType) -> tuple[int, int, int, int]:
        match zone_type:
            case NodeType.NORMAL:
                return pygame.color.THECOLORS["grey25"]
            case NodeType.PRIORITY:
                return pygame.color.THECOLORS["yellow3"]
            case NodeType.BLOCKED:
                return pygame.color.THECOLORS["orangered3"]
            case NodeType.RESTRICTED:
                return pygame.color.THECOLORS["violetred2"]

    @staticmethod
    def get_pos(
        pos: Node | Connection | None,
    ) -> Vector2:

        pos_res = Vector2()
        if isinstance(pos, Connection):
            pos_res = (
                pos.from_node.pos.elementwise()
                + pos.to_node.pos) / 2
        elif isinstance(pos, Node):
            pos_res = pos.pos

        return pos_res

    @staticmethod
    def move_from_a_to_b(
            a: Vector2, b: Vector2) -> Generator[Vector2, None, None]:
        factor_of_division = 50

        x = (-a.x + b.x) / factor_of_division
        y = (-a.y + b.y) / factor_of_division

        pos = Vector2(x, y)
        res = a
        for _ in range(factor_of_division):
            res = res.elementwise() + pos
            yield res
