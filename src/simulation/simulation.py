from ..parser.config import Config, Hub, Drone

# Forbid this for now
schedular = {}


def add_zone(zone_name: str, list_of_options: list[Hub]) -> None:
    made_list = list()
    for hub in list_of_options:
        made_list.append(list([hub, 0]))

    if schedular.get(zone_name) is None:
        schedular[zone_name] = made_list
    else:
        schedular[zone_name] = [i for i in schedular[zone_name] if i[0] in list_of_options]


def schedular_func(zone_name: str) -> Hub:
    if not any([d[1] for d in schedular[zone_name]]):
        schedular[zone_name][0][1] = 1
        return schedular[zone_name][0][0]
    for i, option in enumerate(schedular[zone_name]):
        if option[1] == 1:
            schedular[zone_name][i][1] = 0
            if i == len(schedular[zone_name]) - 1:
                schedular[zone_name][0][1] = 1
                return schedular[zone_name][0][0]
            else:
                schedular[zone_name][i + 1][1] = 1
                return schedular[zone_name][i + 1][0]


def hub_logic(drone: Drone) -> bool:
    lowest_cost_zones = []
    is_waiting = True

    # ! This could be wrong in the future needs testing
    if drone.on_connection:
        return False

    # From current hub check all connections.
    for con in drone.position.connections:

        # Get opposite zone of connection.
        if con.from_zone.name == drone.position.name:
            zone = con.to_zone
        else:
            zone = con.from_zone

        # Connection or Hub is already at max capacity ignore connection/zone.
        if len(con.drones) >= con.max_link_capacity:
            print("LOG: Max link capacity reached")
            continue
        if len(zone.drones) >= zone.metadata.max_drones:
            print("LOG: Max drone reached")
            continue

        # Set first zone as reference
        if len(lowest_cost_zones) == 0:
            # print("!!!!!!!!!!!!!!!!!!!!!!!")
            lowest_cost_zones.append(zone)
        # If found zone with lower cost clear list and insert new zone
        elif zone.cost < lowest_cost_zones[0].cost:
            lowest_cost_zones = [zone]
        # If same cost add to list so we got options to pick from.
        elif zone.cost == lowest_cost_zones[0].cost:
            lowest_cost_zones.append(zone)

        is_waiting = False


    if is_waiting or drone.position.cost <= lowest_cost_zones[0].cost:
        return is_waiting

    if len(lowest_cost_zones) == 1:
        drone.next_step = lowest_cost_zones[0]
        print(drone.next_step.name)
        return is_waiting

    if len(lowest_cost_zones) > 1:
        print(len(lowest_cost_zones))
        add_zone(drone.position.name, lowest_cost_zones)
        drone.next_step = schedular_func(drone.position.name)
    # print(drone.next_step.name)




def simulation(config: Config) -> list[list[tuple[str, str]]]:

    # Max turns before simulation automatically closes itself
    max_run = float("inf")

    # Can maybe be replaced by max run
    simulation_running = True

    drones: list[Drone] = []

    # Populate the drone list.
    for i in range(config.nb_drones):
        drones.append(Drone(id=i+1, position=config.start_hub, next_step=config.start_hub))

    # Holds information about events.
    action_log = []

    while simulation_running:

        max_run -= 1
        round = []

        if max_run == 0:
            print("LOG: Simulation was closed by max simulation count")
            return action_log

        # All drones reached end goal.
        # TODO: Could be moved to while loop.
        if not drones:
            return action_log

        # Sort the list so the drones move in order from goal to start.
        # This is helpful so the drones behind are already aware of the new location of the drones in front.
        # ! I think this is useless as the drones that started first should always be future ahead anyway.
        # drones.sort(key=lambda x: x.next_step.cost)

        # Copy so we do not have conflicts in changing the list while we go over it.
        copy_of_drones = drones.copy()
        # copy_of_drones = drones

        # Clear connection occupations of normal connections.
        # TODO: This should not need a clearing like this it would be better to just do it proper. I dont know how yet tho
        for connection in config.connections:
            # if not connection.from_zone.metadata.zone.value == "restricted" and not connection.to_zone.metadata.zone.value == "restricted":
            connection.drones.clear()

        for drone in copy_of_drones:

            is_waiting = hub_logic(drone)

            # This should happen only if there is no move at all the drone could do. Needs changing as well.
            if is_waiting:
                print(f"LOG: {drone.id} is waiting")
                continue

            # Remove occupation of zone before.
            if drone.position.drones.get(drone.id) is not None:
                drone.position.drones.pop(drone.id)

            # Log
            if isinstance(drone.position, Hub):
                for con in drone.next_step.connections:
                    if drone.position.name == con.from_zone.name and drone.next_step.name == con.to_zone.name:
                        con.drones[drone.id] = drone
                        print("Connection got added")
                    elif drone.position.name == con.to_zone.name and drone.next_step.name == con.from_zone.name:
                        print("Connection got added")

                        con.drones[drone.id] = drone
                    

            if drone.next_step.metadata.zone.value == "restricted" and not drone.on_connection:
                for con in drone.next_step.connections:
                    if con.from_zone.name == drone.position.name and con.to_zone.name == drone.next_step.name:
                        drone.position = con
                        drone.on_connection = True
                        sel_con = con
                        break
                    elif con.to_zone.name == drone.position.name and con.from_zone.name == drone.next_step.name:
                        drone.position = con
                        drone.on_connection = True
                        sel_con = con
                        break
                round.append((f"D{drone.id}", f"{sel_con.from_zone.name}-{sel_con.to_zone.name}"))

            else:
                drone.on_connection = False
                drone.position = drone.next_step
                round.append((f"D{drone.id}", drone.position.name))


            drone.position.drones[drone.id] = drone

            print(drone.id, len(drone.position.drones))

            if isinstance(drone.position, Hub) and drone.position.name == config.end_hub.name:
                drone.position.drones.pop(drone.id)
                drones.remove(drone)
                print("POPPP")

        for connection in config.connections:
            # if not connection.from_zone.metadata.zone.value == "restricted" and not connection.to_zone.metadata.zone.value == "restricted":
            connection.drones.clear()
        action_log.append(round)
