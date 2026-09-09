from src.models import NodeType, Node, Connection
import pygame
from pygame import Vector2
from typing import Generator


class RenderHelper:
    @staticmethod
    def _get_zone_type_color(zone_type: NodeType) -> pygame.color.Color:
        match zone_type:
            case NodeType.NORMAL:
                return pygame.color.THECOLORS["black"]
            case NodeType.PRIORITY:
                return pygame.color.THECOLORS["yellow"]
            case NodeType.BLOCKED:
                return pygame.color.THECOLORS["red"]
            case NodeType.RESTRICTED:
                return pygame.color.THECOLORS["orange"]

    @staticmethod
    def get_pos(
        current_pos: Node | Connection,
        next_pos: Node | Connection
    ) -> tuple[Vector2, Vector2]:

        current_pos_res = None
        next_pos_res = None
        if isinstance(current_pos, Connection):
            current_pos_res = (
                current_pos.from_node.pos.elementwise()
                + current_pos.to_node.pos) / 2
        elif isinstance(current_pos, Node):
            current_pos_res = current_pos.pos

        if isinstance(next_pos, Connection):
            next_pos_res = (
                next_pos.from_node.pos.elementwise()
                + next_pos.to_node.pos) / 2
        elif isinstance(next_pos, Node):
            next_pos_res = next_pos.pos
        return (current_pos_res, next_pos_res)

    @staticmethod
    def _move_from_a_to_b(a: Vector2, b: Vector2
                          ) -> Generator[Vector2, None, None]:
        factor_of_division = 50

        x = (-a.x + b.x) / factor_of_division
        y = (-a.y + b.y) / factor_of_division

        pos = Vector2(x, y)
        res = a
        for _ in range(factor_of_division):
            res = res.elementwise() + pos
            yield res
