import pygame
from pygame.locals import *
from ..parser import Config


class Pos:
    min_val: int
    max_val: int
    difference: int


class PosValues:
    def __init__(self, x: Pos, y: Pos):
        self.x = x
        self.y = y


class Scale:
    def __init__(self, x_scale: int, y_scale: int, scale: int):
        self.x_scale = x_scale
        self.y_scale = y_scale

        self.scale = scale


def render_lines(config: Config, pos_values: PosValues, screen, scale) -> None:

    line_thickness = int(0.1 * scale.scale)
    # todo: Make this once and not every time
    for connection in config.connections:
        zone_x, zone_y = connection.from_zone.coordinate

        start_pos_x = (zone_x + pos_values.x.min_val)*scale.x_scale
        start_pos_y = (zone_y + pos_values.y.min_val)*scale.y_scale

        zone_x, zone_y = connection.to_zone.coordinate

        end_pos_x = (zone_x + pos_values.x.min_val)*scale.x_scale
        end_pos_y = (zone_y + pos_values.y.min_val)*scale.y_scale

        if connection.from_zone.metadata.zone.value == "priority" or connection.to_zone.metadata.zone.value == "priority":
            pygame.draw.line(screen, "gold", [start_pos_x, start_pos_y], [end_pos_x, end_pos_y], line_thickness)
        elif connection.from_zone.metadata.zone.value == "blocked" or connection.to_zone.metadata.zone.value == "blocked":
            pygame.draw.line(screen, "red", [start_pos_x, start_pos_y], [end_pos_x, end_pos_y], line_thickness)
        elif connection.from_zone.metadata.zone.value == "restricted" or connection.to_zone.metadata.zone.value == "restricted":
            pygame.draw.line(screen, "blue", [start_pos_x, start_pos_y], [end_pos_x, end_pos_y], line_thickness)
        else:
            pygame.draw.line(screen, "black", [start_pos_x, start_pos_y], [end_pos_x, end_pos_y], line_thickness)


def render_circle(config, pos_values: PosValues, screen, text_font, scale):
    circle_radius = 0.3 * scale.scale

    for zone in config.zones.values():

        zone_x, zone_y = zone.coordinate

        pos_x = (zone_x + pos_values.x.min_val)*scale.x_scale
        pos_y = (zone_y + pos_values.y.min_val)*scale.y_scale

        pygame.draw.circle(screen, zone.metadata.color.value, [pos_x, pos_y], circle_radius)

        img = text_font.render(str(zone.cost), True, "black")
        screen.blit(img, [pos_x, pos_y])
        # print(zone.name, zone.coordinate, pos_x, pos_y)


def visual_logic(config: Config, pos_values: PosValues, screen, text_font, scale):

    # Render lines
    render_lines(config, pos_values, screen, scale)

    # # Render circle.
    render_circle(config, pos_values, screen, text_font, scale)


def visual_worker(config: Config):

    pygame.init()

    screen_resolution = pygame.display.get_desktop_sizes()[0]
    screen = pygame.display.set_mode(screen_resolution, pygame.RESIZABLE)

    pygame.display.toggle_fullscreen()
    pygame.display.set_caption("Fly in visual")

    clock = pygame.time.Clock()

    # Scale logic
    pos_values = possition_calc(config)

    while True:
        # Process player inputs.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        # Do logical updates here.
        key = pygame.key.get_just_pressed()
        if key[K_ESCAPE]:
            pygame.event.pump(pygame.QUIT)
        elif key[K_F11]:
            pygame.display.toggle_fullscreen()

        screen_resolution = pygame.display.get_window_size()

        scale = scale_calc(pos_values, screen_resolution)
        text_font = pygame.font.SysFont("Arial", int(0.15 * scale.scale))


        screen.fill("white")  # Fill the display with a solid color

        # Render the graphics here.
        visual_logic(config, pos_values, screen, text_font, scale)

        pygame.display.update()
        clock.tick(60)         # wait until next frame (at 60 FPS)


def possition_calc(config: Config) -> PosValues:
    x_pos = Pos()

    x_pos.min_val = min(zone.coordinate[0] for zone in config.zones.values())
    x_pos.max_val = max(zone.coordinate[0] for zone in config.zones.values())
    x_pos.difference = abs(x_pos.max_val - x_pos.min_val)
    if x_pos.difference == 0:
        x_pos.difference = 1
    else:
        x_pos.difference += 1

    y_pos = Pos()

    y_pos.min_val = min(zone.coordinate[1] for zone in config.zones.values())
    y_pos.max_val = max(zone.coordinate[1] for zone in config.zones.values())
    y_pos.difference = abs(y_pos.max_val - y_pos.min_val)
    if y_pos.difference == 0:
        y_pos.difference = 1
    else:
        y_pos.difference += 1

    x_pos.min_val = abs(x_pos.min_val) + 0.5
    y_pos.min_val = abs(y_pos.min_val) + 0.5

    return PosValues(x_pos, y_pos)

def scale_calc(pos_values: PosValues, screen_resolution):
    x_scale = (screen_resolution[0] // pos_values.x.difference)
    y_scale = (screen_resolution[1] // pos_values.y.difference)

    scale = ((screen_resolution[0] + screen_resolution[1]) // (pos_values.x.difference + pos_values.y.difference))
    return Scale(x_scale, y_scale, scale)
