from .models import Scale, Pos_values, Vector2
from src.models import Config, Hub, Connection
import pygame
from typing import Generator


class Render:
    def __init__(self, config: Config, scale: Scale, pos_values: Pos_values, screen, action_log: list[dict[int, Hub | Connection]]):
        self.config = config
        self.scale = scale
        self.pos_values = pos_values
        self.screen = screen
        self.animation = False
        self.action_log = action_log
        self.index = 0

    @staticmethod
    def get_pos(current_pos: Hub | Connection, next_pos: Hub | Connection) -> tuple[Vector2, Vector2]:
        current_pos_res = None
        next_pos_res = None
        if isinstance(current_pos, Connection):
            current_pos_res = (current_pos.from_zone.pos.elementwise() + current_pos.to_zone.pos) / 2
        elif isinstance(current_pos, Hub):
            current_pos_res = current_pos.pos

        if isinstance(next_pos, Connection):
            next_pos_res = (next_pos.from_zone.pos.elementwise() + next_pos.to_zone.pos) / 2
        elif isinstance(next_pos, Hub):
            next_pos_res = next_pos.pos
        return (current_pos_res, next_pos_res)

    @staticmethod
    def move_from_a_to_b(a: Vector2, b: Vector2) -> Generator[Vector2, None, None]:
        factor_of_division = 50

        x = (-a.x + b.x) / factor_of_division
        y = (-a.y + b.y) / factor_of_division

        pos = Vector2(x, y)
        res = a
        for _ in range(factor_of_division):
            res = res.elementwise() + pos
            yield res

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
            a = con.from_zone.pos.elementwise() * self.scale.pos
            b = con.to_zone.pos.elementwise() * self.scale.pos

            pygame.draw.line(self.screen, "black", a, b, line_thickness)

            img = self.font.render(
                f"{len(con.drones)}/{con.max_link_capacity}",
                True, "white",
                bgcolor="darkslategray"
            )
            self.screen.blit(img, img.get_rect(
                center=((a.x + b.x) // 2, ((a.y + b.y) // 2))))

    def _render_zone(self):
        circle_radius = 0.3 * self.scale.full_scale

        for zone in self.config.zones.values():

            a = zone.pos.elementwise() * self.scale.pos

            pygame.draw.circle(
                self.screen, zone.metadata.color, a, circle_radius)

            img = self.font.render(str(zone.cost), True, "black")
            self.screen.blit(img, a)

            # Display zone name
            img = self.font.render(
                str(zone.name),
                True,
                "white",
                bgcolor="darkslategray"
            )
            self.screen.blit(img, img.get_rect(center=a.elementwise() + Vector2(0, -10)))

            # Display zone capacity
            img = self.font.render(
                f"{len(zone.drones)}/{zone.metadata.max_drones}",
                True,
                "white",
                bgcolor="darkslategray"
            )
            self.screen.blit(
                img,
                img.get_rect(
                    center=(a.x, int(a.y + 0.15 * self.scale.full_scale)))
            )

    def _render_drone(self) -> bool:
        rect_size = 0.25 * self.scale.full_scale
        animation = True
        count = 0
        content = None

        for drone in self.config.drones:
            if drone.position == self.config.end_hub:
                continue
            # pos = (0, 0)
            # offset = False

            if self.animation:
                if (content := self.action_log[self.index].get(drone.id)):
                    # Get drone from list
                    drone.position.drones.pop(drone.id)

                    current_pos = drone.position
                    drone.next_step = content
                    if isinstance(content, Connection):
                        drone.next_step.drones[drone.id] = drone
                    next_pos = drone.next_step = content

                    # print("!!!!!!!!!", current_pos, next_pos)
                    current_pos, next_pos = self.get_pos(current_pos, next_pos)
                    drone.generator = self.move_from_a_to_b(current_pos, next_pos)

            else:
                pos, _ = self.get_pos(drone.next_step, None)
                a = pos.elementwise() * self.scale.pos

            if drone.generator:
                try:
                    a = next(drone.generator)
                    print(a)
                    a = a.elementwise() * self.scale.pos

                    # TODO: get connection and occupy it.
                    for con in self.config.connections:
                        if drone.position == con.to_zone and drone.next_step == con.from_zone \
                            or drone.next_step == con.to_zone and drone.position == con.from_zone:
                            con.drones[drone.id] = drone

                except StopIteration:
                    drone.generator = None
                    print("Drone animation is finished")
                    # TODO: Get connection and clear it.
                    for con in self.config.connections:
                        if drone.position == con.to_zone and drone.next_step == con.from_zone \
                            or drone.next_step == con.to_zone and drone.position == con.from_zone:
                            con.drones.pop(drone.id)
                    drone.position = drone.next_step
                    drone.position.drones[drone.id] = drone
                    count += 1


            # print(pos_x - rect_size // 2, pos_y - rect_size // 2)
            pygame.draw.rect(self.screen, "black", pygame.Rect(a.x - rect_size // 2, a.y - rect_size // 2 - 8, rect_size, rect_size))


            img = self.font.render(str(drone.id), True, "white", bgcolor="darkslategray")
            self.screen.blit(img, img.get_rect(center = a))

            # img = text_font.render(f"{len(zone.drones)}/{zone.metadata.max_drones}", True, "white", bgcolor="darkslategray")
            # screen.blit(img, img.get_rect(center = (pos_x, int(pos_y + 0.15*scale.scale))))

        self.animation = False
        if count == (len(self.action_log[self.index])) or not any(drone.generator for drone in self.config.drones):
            return False
        return True


    def _scale_calc(self) -> None:
        screen_resolution = Vector2(pygame.display.get_window_size())
        self.scale.pos = screen_resolution.elementwise() // self.pos_values.difference
        self.scale.full_scale = (sum(screen_resolution) // sum(self.pos_values.difference))

    def start_animation(self, i) -> bool:
        self.animation = True
        self.index += i
        if self.index == -1 or self.index == len(self.action_log):
            self.index = 0
            for drone in self.config.drones:
                self.config.start_hub.drones[drone.id] = drone
                drone.position = self.config.start_hub
                drone.next_step = self.config.start_hub

