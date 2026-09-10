from src.models import Scale, Pos_values, Config, Node, Connection, \
      Drone
import pygame
from pygame import Vector2
from src.visual.helper import RenderHelper as help
from src.simulation.helper import SimulationHelper as simhelp
from typing import Generator


class Render:
    def __init__(
            self,
            config: Config,
            scale: Scale,
            pos_values: Pos_values,
            screen: pygame.Surface,
            action_log: list[dict[int, Node | Connection]]
    ) -> None:
        self._config = config
        self._scale = scale
        self._pos_values = pos_values
        self._screen = screen
        self._animation_gen = False
        self._action_log = action_log
        self._index = 0
        self._reverse: bool = False

    def visual_logic(self) -> bool:
        self._screen.fill("white")

        self._scale_calc()

        font = pygame.font.SysFont("Arial", int(0.10 * self._scale.full_scale))
        self._font = font

        self._render_lines()
        self._render_zone()

        img = self._font.render(
            f"{self._index}/{len(self._action_log) - 1}",
            True, "white",
            bgcolor="darkslategray"
        )
        self._screen.blit(img, Vector2(5, 5))
        res = self._render_drone()
        self._reverse = False
        return res

    def _render_lines(self) -> None:
        line_thickness = int(0.1 * self._scale.full_scale)

        for con in self._config.connections:
            a = con.from_node.pos.elementwise() * self._scale.pos
            b = con.to_node.pos.elementwise() * self._scale.pos

            pygame.draw.aaline(self._screen, "black", a, b, line_thickness)

            img = self._font.render(
                f"{len(con.drones)}/{con.max_link_capacity}",
                True, "white",
                bgcolor="darkslategray"
            )
            self._screen.blit(img, img.get_rect(
                center=((a.x + b.x) / 2, ((a.y + b.y) / 2))))

    def _render_zone(self) -> None:
        circle_radius = 0.3 * self._scale.full_scale
        offset_text = 0.15 * self._scale.full_scale
        offset_outline = 0.05 * self._scale.full_scale

        for node in self._config.nodes.values():
            a = node.pos.elementwise() * self._scale.pos
            self._render_zone_circle(node, circle_radius, offset_outline, a)

            zone_cost_txt = self._font.render(
                str(int(node.cost)), True, "black", bgcolor="white")
            zone_name_text = self._font.render(
                str(node.name),
                True,
                "white",
                bgcolor="darkslategray"
            )
            zone_capacity_text = self._font.render(
                f"{len(node.drones)}/{node.metadata.max_drones}",
                True,
                "white",
                bgcolor="darkslategray"
            )

            self._screen.blit(
                zone_cost_txt,
                zone_cost_txt.get_rect(
                    center=a.elementwise() + Vector2(0, -offset_text)))
            self._screen.blit(
                zone_name_text, zone_name_text.get_rect(center=a)
            )
            self._screen.blit(
                zone_capacity_text,
                zone_capacity_text.get_rect(
                    center=(a.x, int(a.y + 0.15 * self._scale.full_scale)))
            )

    def _render_drone(self) -> bool:
        rect_size = 0.25 * self._scale.full_scale
        count = 0

        for drone in self._config.drones:
            a = Vector2(0, 0)
            if drone.position == self._config.end_node:
                # if not self._reverse:
                continue

            if self._animation_gen:
                self._animation(drone)
            else:
                pos, _ = help.get_pos(drone.next_step, None)
                a = pos.elementwise() * self._scale.pos

            if drone.generator:
                if (new_pos := self._move_visual(drone, a, drone.generator)):
                    a = new_pos
                else:
                    count += 1

            pygame.draw.rect(
                self._screen,
                "black",
                pygame.Rect(
                    a.x - rect_size / 2,
                    a.y - rect_size / 2,
                    rect_size, rect_size
                )
            )

            img = self._font.render(
                str(drone.id), True, "white", bgcolor="darkslategray")
            self._screen.blit(img, img.get_rect(center=a))

        self._animation_gen = False
        if count == (len(self._action_log[self._index])) \
                or not any(drone.generator for drone in self._config.drones):
            return False
        return True

    def _render_zone_circle(self, node: Node, circle_radius: float,
                            offset_outline: float, a: Vector2) -> None:
        pygame.draw.circle(
            self._screen,
            help.get_zone_type_color(node.metadata.zone),
            a,
            circle_radius
        )
        pygame.draw.circle(
            self._screen,
            node.metadata.color,
            a,
            circle_radius - offset_outline
        )

    def _move_visual(
            self, drone: Drone, a: Vector2,
            generator: Generator[Vector2, None, None]) -> Vector2 | None:
        try:
            a = next(generator)
            a = a.elementwise() * self._scale.pos

            con = simhelp.get_connection_to_next_step(
                self._config.connections,
                drone.position,
                drone.next_step
            )
            con.drones[drone.id] = drone
        except StopIteration:
            drone.generator = None
            simhelp.clear_connection(drone)
            print(drone.id, drone.position.name, drone.next_step.name)
            drone.position = drone.next_step
            drone.position.drones[drone.id] = drone
            return None
        return a

    def _animation(self, drone: Drone) -> None:
        if (content := self._action_log[self._index].get(drone.id)):
            drone.next_step = content

            if isinstance(content, Connection):
                drone.next_step.drones[drone.id] = drone
            else:
                if isinstance(drone.position, Node):
                    drone.position.drones.pop(drone.id)

            current_pos, next_pos = help.get_pos(drone.position, content)
            drone.generator = help.move_from_a_to_b(current_pos, next_pos)

    def _scale_calc(self) -> None:
        screen_resolution = Vector2(pygame.display.get_window_size())
        self._scale.pos = (
            screen_resolution.elementwise() / self._pos_values.difference)

        self._scale.full_scale = int(
            sum(screen_resolution) / sum(self._pos_values.difference))

    def _start_animation(self, i: int) -> None:
        self._animation_gen = True
        self._index += i
        if i < 0:
            self._reverse = True
        if self._index == -1 or self._index == len(self._action_log):
            self._index = 0
            for drone in self._config.drones:
                self._config.start_node.drones[drone.id] = drone
                drone.position = self._config.start_node
                drone.next_step = self._config.start_node

    def _reset(self) -> None:
        [con.drones.clear() for con in self._config.connections]
        [node.drones.clear() for node in self._config.nodes.values()]
        for drone in self._config.drones:
            drone.position = self._config.start_node
            drone.next_step = self._config.start_node
            drone.position.drones[drone.id] = drone
        self._index = 0
