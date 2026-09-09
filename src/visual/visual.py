import pygame
import pygame.locals

from ..parser import Config

from .models import Pos_values, Scale, Vector2
from .render import Render


def normalize_coords(pos: Vector2, pos_values: Pos_values) -> Vector2:
    return pos.elementwise() + pos_values.min_val


def position_calc(config: Config) -> Pos_values:
    min_val = Vector2()
    max_val = Vector2()
    difference = Vector2()

    min_val.x = min(zone.pos.x for zone in config.nodes.values())
    max_val.x = max(zone.pos.x for zone in config.nodes.values())

    min_val.y = min(zone.pos.y for zone in config.nodes.values())
    max_val.y = max(zone.pos.y for zone in config.nodes.values())

    difference.x = abs(max_val.x - min_val.x)
    difference.y = abs(max_val.y - min_val.y)

    if difference.x == 0:
        difference.x = 1
    else:
        difference.x += 1

    if difference.y == 0:
        difference.y = 1
    else:
        difference.y += 1

    min_val.x = abs(min_val.x) + 0.5
    min_val.y = abs(min_val.y) + 0.5

    return Pos_values(min_val, max_val, difference)


def map_prepping(config: Config, pos_values: Pos_values, action_log: list[list[tuple[str, str]]]):
    for zone in config.nodes.values():
        zone.pos = normalize_coords(zone.pos, pos_values)

    for drone in config.drones:
        drone.active = True
        drone.position = config.start_node
        drone.next_step = config.start_node
        config.start_node.drones[drone.id] = drone

    bla_list = {}
    for drone in config.drones:
        bla_list.update({drone.id: config.start_node})
    action_log.insert(0, bla_list)


def init(config, action_log) -> Render:
    pygame.init()

    screen_resolution = pygame.display.get_desktop_sizes()[0]
    screen = pygame.display.set_mode(screen_resolution, pygame.RESIZABLE)

    pygame.display.toggle_fullscreen()
    pygame.display.set_caption("Fly in visual")

    # Scale logic
    scale = Scale(Vector2(0, 0), 0)
    pos_values = position_calc(config)

    map_prepping(config, pos_values, action_log)

    screen_resolution = Vector2(pygame.display.get_window_size())
    return Render(config, scale, pos_values, screen, action_log)


def visual_worker(config: Config, action_logs: list[list[tuple[str, str]]]):

    render = init(config, action_logs)
    clock = pygame.time.Clock()

    selected = 0
    in_animation = False
    automatic_animation = False
    waiting_time = 50

    print(len(config.start_node.drones))
    while True:
        # Process player inputs.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == 111 and not in_animation:
                render._start_animation(1)

        # Do logical updates here.
        key = pygame.key.get_just_pressed()
        if key[pygame.locals.K_ESCAPE]:
            pygame.event.pump(pygame.QUIT)
        elif key[pygame.locals.K_F11]:
            pygame.display.toggle_fullscreen()
        elif key[pygame.locals.K_RIGHT]:
            if not in_animation:
                render._start_animation(1)
        elif key[pygame.locals.K_LEFT]:
            if not in_animation:
                render._start_animation(-1)

        elif key[pygame.locals.K_UP]:
            waiting_time -= 50
            pygame.time.set_timer(111, waiting_time)

        elif key[pygame.locals.K_DOWN]:
            waiting_time += 50
            pygame.time.set_timer(111, waiting_time)

        elif key[pygame.locals.K_SPACE]:
            if automatic_animation or in_animation:
                pygame.time.set_timer(111, 0)
            else:
                pygame.time.set_timer(111, waiting_time)



        action_log = action_logs[selected]

        # Render the graphics here.

        in_animation = render.visual_logic()

        pygame.display.update()
        clock.tick(60)
