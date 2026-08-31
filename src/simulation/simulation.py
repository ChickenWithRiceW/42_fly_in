from ..parser.config import Config, Connection, Hub, Drone



def hub_logic(drone: Drone) -> bool:
    lowest_cost_zone = None
    is_waiting = True

    if drone.on_connection:
        # drone.on_connection = False
        # drone.position = drone.next_step
        # drone.next_step = None
        return False

    for con in drone.position.connections:

        if con.from_zone.name == drone.position.name:
            zone = con.to_zone
        else:
            zone = con.from_zone

        # If connection or Hub is already at max capacity.
        if len(con.drones) >= con.max_link_capacity:
            print("max link capacity reached")
            continue
        if len(zone.drones) >= zone.metadata.max_drones:
            print("max drone reached")

            continue

        if lowest_cost_zone is None:
            lowest_cost_zone = zone

        if zone.cost < lowest_cost_zone.cost:
            lowest_cost_zone = zone

        is_waiting = False
        drone.next_step = lowest_cost_zone
    return is_waiting


def simulation(config: Config):
    simulation_running = True

    drones: list[Drone] = []

    # Populate the drone list.
    for i in range(config.nb_drones):
        drones.append(Drone(id=i+1, position=config.start_hub, next_step=config.start_hub))

    # Holds information about events.
    action_log = []

    # No restricted zones yet.
    while simulation_running:

        round = []

        # All drones reached end goal.
        if not drones:
            return action_log

        # Sort the list so the drones move in order from goal to start.
        # This is helpful so the drones behind are already aware of the new location of the drones in front.
        drones.sort(key=lambda x: x.next_step.cost)

        # Copy so we do not have conflicts in changing the list while we go over it.
        copy_of_drones = drones.copy()


        for connection in config.connections:
            if not connection.from_zone.metadata.zone.value == "restricted" and not connection.to_zone.metadata.zone.value == "restricted":
                connection.drones.clear()
        for i, drone in enumerate(copy_of_drones):

            # if isinstance(drone.position, Hub):
            is_waiting = hub_logic(drone)
            # elif isinstance(drone.position, Connection):
            #     is_waiting

            if is_waiting:
                print(drone.id, "is waiting")
                continue

            if drone.position.drones.get(drone.id):
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
                drones.pop(i)
                print("POPPP")

        action_log.append(round)
