from .models import Scale, Pos_values, Vector2
from src.models import Config, Node, Connection, Drone
import pygame
from typing import Generator
from src.simulation.helper import SimulationHelper as helper


class Render:
    def __init__(self, config: Config, scale: Scale, pos_values: Pos_values,
                 screen, action_log: list[dict[int, Node | Connection]]):
        self.config = config
        self.scale = scale
        self.pos_values = pos_values
        self.screen = screen
        self.animation = False
        self.action_log = action_log
        self.index = 0

    def visual_logic(self) -> bool:
        self.screen.fill("white")

        self._scale_calc()

        font = pygame.font.SysFont("Arial", int(0.10 * self.scale.full_scale))
        self.font = font

        self._render_lines()
        self._render_zone()

        img = self.font.render(
            f"{self.index}/{len(self.action_log) - 1}",
            True, "white",
            bgcolor="darkslategray"
        )
        self.screen.blit(img, Vector2(5, 5))
        return self._render_drone()

    def _render_lines(self) -> None:
        line_thickness = int(0.1 * self.scale.full_scale)

        for con in self.config.connections:
            a = con.from_node.pos.elementwise() * self.scale.pos
            b = con.to_node.pos.elementwise() * self.scale.pos

            pygame.draw.aaline(self.screen, "black", a, b, line_thickness)

            img = self.font.render(
                f"{len(con.drones)}/{con.max_link_capacity}",
                True, "white",
                bgcolor="darkslategray"
            )
            self.screen.blit(img, img.get_rect(
                center=((a.x + b.x) // 2, ((a.y + b.y) // 2))))

    def _render_zone(self):
        circle_radius = 0.3 * self.scale.full_scale

        for node in self.config.nodes.values():
            a = node.pos.elementwise() * self.scale.pos
            self._render_zone_circle(node, circle_radius, a)

            zone_cost_txt = self.font.render(str(node.cost), True, "black")
            zone_name_text = self.font.render(
                str(node.name),
                True,
                "white",
                bgcolor="darkslategray"
            )
            zone_capacity_text = self.font.render(
                f"{len(node.drones)}/{node.metadata.max_drones}",
                True,
                "white",
                bgcolor="darkslategray"
            )

            self.screen.blit(
                zone_cost_txt,
                zone_cost_txt.get_rect(
                    center=a.elementwise() + Vector2(0, -circle_radius + 40)))

            self.screen.blit(
                zone_name_text, zone_name_text.get_rect(center=a.elementwise() + Vector2(0, -10))
            )

            self.screen.blit(
                zone_capacity_text,
                zone_capacity_text.get_rect(
                    center=(a.x, int(a.y + 0.15 * self.scale.full_scale)))
            )

    def _render_drone(self) -> bool:
        rect_size = 0.25 * self.scale.full_scale
        count = 0

        for drone in self.config.drones:
            if drone.position == self.config.end_node:
                continue

            if self.animation:
                self._animation(drone)
            else:
                pos, _ = self.get_pos(drone.next_step, None)
                a = pos.elementwise() * self.scale.pos

            if drone.generator:
                try:
                    a = next(drone.generator)
                    a = a.elementwise() * self.scale.pos

                    con = helper._get_connection_to_next_step(
                        self.config.connections,
                        drone.position,
                        drone.next_step
                    )
                    con.drones[drone.id] = drone
                except StopIteration:
                    drone.generator = None
                    helper._clear_connection(drone)
                    drone.position = drone.next_step
                    drone.position.drones[drone.id] = drone
                    count += 1


            pygame.draw.rect(self.screen, "black", pygame.Rect(a.x - rect_size // 2, a.y - rect_size // 2 - 8, rect_size, rect_size))
            img = self.font.render(str(drone.id), True, "white", bgcolor="darkslategray")
            self.screen.blit(img, img.get_rect(center = a))


        self.animation = False
        if count == (len(self.action_log[self.index])) or not any(drone.generator for drone in self.config.drones):
            return False
        return True

    def _render_zone_circle(self, node: Node, circle_radius: int, a: Vector2):
        pygame.draw.circle(
            self.screen,
            self._get_zone_type_color(node.metadata.zone),
            a,
            circle_radius
        )
        pygame.draw.circle(
            self.screen, node.metadata.color, a, circle_radius - 10)

    def _animation(self, drone: Drone):
        if (content := self.action_log[self.index].get(drone.id)):
            drone.position.drones.pop(drone.id)

            drone.next_step = content
            if isinstance(content, Connection):
                drone.next_step.drones[drone.id] = drone

            current_pos, next_pos = self.get_pos(drone.position, content)
            drone.generator = self._move_from_a_to_b(current_pos, next_pos)

    def _scale_calc(self) -> None:
        screen_resolution = Vector2(pygame.display.get_window_size())
        self.scale.pos = screen_resolution.elementwise() // self.pos_values.difference
        self.scale.full_scale = (sum(screen_resolution) // sum(self.pos_values.difference))

    def _start_animation(self, i) -> bool:
        self.animation = True
        self.index += i
        if self.index == -1 or self.index == len(self.action_log):
            self.index = 0
            for drone in self.config.drones:
                self.config.start_node.drones[drone.id] = drone
                drone.position = self.config.start_node
                drone.next_step = self.config.start_node
