import pygame
from pygame.locals import *
from ..parser import Config
from .code_rip import draw_arrow



def render_lines(config: Config, screen_resolution, x_difference, y_difference, x_min, y_min, screen) -> None:
    for connection in config.connections:
        zone_x, zone_y = connection.from_zone.coordinate

        s_pos_x = (screen_resolution[0] / x_difference) / 1
        zone_x = zone_x + abs(x_min) + 0.5
        s_pos_x = s_pos_x * zone_x

        s_pos_y = (screen_resolution[1] / y_difference) / 1
        zone_y = zone_y + abs(y_min) + 0.5
        s_pos_y = s_pos_y * zone_y

        zone_x, zone_y = connection.to_zone.coordinate

        e_pos_x = (screen_resolution[0] / x_difference) / 1
        zone_x = zone_x + abs(x_min) + 0.5
        e_pos_x = e_pos_x * zone_x

        e_pos_y = (screen_resolution[1] / y_difference) / 1
        zone_y = zone_y + abs(y_min) + 0.5
        e_pos_y = e_pos_y * zone_y


        if connection.from_zone.metadata.zone.value == "priority" or connection.to_zone.metadata.zone.value == "priority":
            pygame.draw.line(screen, "gold", [s_pos_x, s_pos_y], [e_pos_x, e_pos_y], 10)
        elif connection.from_zone.metadata.zone.value == "blocked" or connection.to_zone.metadata.zone.value == "blocked":
            pygame.draw.line(screen, "red", [s_pos_x, s_pos_y], [e_pos_x, e_pos_y], 10)
        else:
            pygame.draw.line(screen, "black", [s_pos_x, s_pos_y], [e_pos_x, e_pos_y], 10)


        # body_width = 0.1*(screen_resolution[0] + screen_resolution[1]) / (x_difference + y_difference)
        # bigger_thing = 0.3*(screen_resolution[0] + screen_resolution[1]) / (x_difference + y_difference)


        # offset = 0.2*(screen_resolution[0] + screen_resolution[1]) / (x_difference + y_difference)

        # if e_pos_x == s_pos_x:
        #     if e_pos_y > s_pos_y:
        #         e_pos_y -= offset
        #         s_pos_y += offset
        #     else:
        #         e_pos_y += offset
        #         s_pos_y -= offset

        # if e_pos_y == s_pos_y:
        #     if e_pos_x > s_pos_x:
        #         e_pos_x -= offset
        #         s_pos_x += offset
        #     else:
        #         e_pos_x += offset
        #         s_pos_x -= offset



        # if connection.direction == 2:
        #     draw_arrow(screen, pygame.Vector2(s_pos_x, s_pos_y), pygame.Vector2(e_pos_x, e_pos_y), "black", body_width, bigger_thing, body_width + 10)
        # elif connection.direction == 1:
        #     draw_arrow(screen, pygame.Vector2(s_pos_x, s_pos_y), pygame.Vector2(e_pos_x, e_pos_y), "blue", body_width, bigger_thing, body_width + 10)
        #     draw_arrow(screen, pygame.Vector2(e_pos_x, e_pos_y), pygame.Vector2(s_pos_x, s_pos_y), "blue", body_width, bigger_thing, body_width + 10)
        # elif connection.direction == 3:
        #     draw_arrow(screen, pygame.Vector2(e_pos_x, e_pos_y), pygame.Vector2(s_pos_x, s_pos_y), "red", body_width, bigger_thing, body_width + 10)
            

        

def visual(config: Config):

    pygame.init()

    screen_resolution = pygame.display.get_desktop_sizes()[0]

    screen = pygame.display.set_mode(screen_resolution, pygame.RESIZABLE)
    pygame.display.toggle_fullscreen()
    pygame.display.set_caption("Fly in visual")

    clock = pygame.time.Clock()

    text_font = pygame.font.SysFont("Arial", 20)


    x_min = min(zone.coordinate[0] for zone in config.zones.values())
    x_max = max(zone.coordinate[0] for zone in config.zones.values())
    x_difference = abs(x_max - x_min)
    if x_difference == 0:
        x_difference = 1
    else:
        x_difference += 1



    y_min = min(zone.coordinate[1] for zone in config.zones.values())
    y_max = max(zone.coordinate[1] for zone in config.zones.values())
    y_difference = abs(y_max - y_min)
    if y_difference == 0:
        y_difference = 1
    else:
        y_difference += 1



    while True:
        # Process player inputs.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        # Do logical updates here.
        # ...
        key = pygame.key.get_just_pressed()
        if key[K_ESCAPE]:
            pygame.event.pump(pygame.QUIT)
        elif key[K_F11]:
            pygame.display.toggle_fullscreen()

        screen_resolution = pygame.display.get_window_size()

        # The circle radius
        circle_radius = 0.2*(screen_resolution[0] + screen_resolution[1]) / (x_difference + y_difference)

        screen.fill("white")  # Fill the display with a solid color

        # Render the graphics here.
        # ...

        render_lines(config, screen_resolution, x_difference, y_difference, x_min, y_min, screen)

        # Render circle.
        for zone in config.zones.values():
            pos_x = (screen_resolution[0] / x_difference) / 1
            zone_x = zone.coordinate[0] + abs(x_min) + 0.5
            pos_x = pos_x * zone_x

            pos_y = (screen_resolution[1] / y_difference) / 1
            zone_y = zone.coordinate[1] + abs(y_min) + 0.5
            pos_y = pos_y * zone_y
            pygame.draw.circle(screen, zone.metadata.color.value, [pos_x, pos_y], circle_radius)

            img = text_font.render(str(zone.cost), True, "black")
            screen.blit(img, [pos_x, pos_y])
            # print(zone.name, zone.coordinate, pos_x, pos_y)




        # pygame.display.flip()  # Refresh on-screen display
        pygame.display.update()
        clock.tick(60)         # wait until next frame (at 60 FPS)
