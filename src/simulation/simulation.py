from src.models import Config, Hub, Drone, Connection, ZoneType
from .schedular import Schedular


def hub_logic(drone: Drone, schedular: Schedular, config: Config) -> bool:
    lowest_cost_zones = []
    is_waiting = True

    if isinstance(drone.position, Connection):
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
            continue
        if len(zone.drones) >= zone.metadata.max_drones:
            continue

        # if len([drones for drones in zone.edge_case.values() if drones.next_step.metadata.zone == ZoneType.RESTRICTED]) == zone.metadata.max_drones:
        #     # print("AHHHHHHHHHHH")
        #     # exit()
        #     continue

        # Set first zone as reference
        if not lowest_cost_zones:
            lowest_cost_zones.append(zone)

        # If found zone with lower cost clear list and insert new zone
        elif zone.cost < lowest_cost_zones[0].cost:
            lowest_cost_zones = [zone]
        # If same cost add to list so we got options to pick from.
        elif zone.cost == lowest_cost_zones[0].cost:
            lowest_cost_zones.append(zone)


        is_waiting = False

    if is_waiting or drone.position.cost <= lowest_cost_zones[0].cost:
        return True

    if len(lowest_cost_zones) == 1:
        drone.next_step = lowest_cost_zones[0]
    else:
        schedular.add_zone(drone.position.name, lowest_cost_zones)
        drone.next_step = config.zones[schedular.schedular_func(drone.position.name)]
    return is_waiting


def simulation(config: Config) -> list[dict[int, Hub | Connection]]:

    drones: list[Drone] = []

    # Populate the drone list.
    for i in range(config.nb_drones):
        drones.append(Drone(id=i, position=config.start_hub, next_step=config.start_hub))

    config.drones = drones

    # Holds information about events.
    action_log = []

    count = 0
    schedular = Schedular()

    while count != config.nb_drones:
        count = 0
        round = {}

        for drone in drones:
            if not drone.active:
                count += 1
                continue
            transit(drone, schedular, config)

        for drone in drones:
            if not drone.active:
                continue

            round.update(finalized(drone, config))

        action_log.append(round)
        # if len(action_log) == 7:
        #     print(len(config.zones["path_c"].edge_case))

    for connection in config.connections:
        connection.drones.clear()
    for hub in config.zones.values():
        hub.drones.clear()
    return action_log



def transit(drone: Drone, schedular, config) -> bool:
    drone.is_waiting = hub_logic(drone, schedular, config)

    if drone.is_waiting:
        print(drone.id, "is waiting")
        return

    # Remove occupation of zone before.
    if isinstance(drone.position, Hub):
        drone.position.drones.pop(drone.id, None)

    # This will occupy the connection between current pos and next pos
    occupy_connection(drone)

    drone.next_step.drones[drone.id] = drone
    # ---------------------------------- THIS IS ALL THE LOGIC NEEDED FROM A TO B




def finalized(drone: Drone, config: Config) -> dict[int, Hub | Connection]:
    if isinstance(drone.position, Hub) and drone.next_step.metadata.zone == ZoneType.RESTRICTED:
        for con in drone.next_step.connections:
            if con.from_zone.name == drone.position.name and con.to_zone.name == drone.next_step.name:
                drone.position = con
                break
            elif con.to_zone.name == drone.position.name and con.from_zone.name == drone.next_step.name:
                drone.position = con
                break
    else:
        clear_connection(drone)
        drone.position = drone.next_step

    # If reached goal drone deactivates.
    if drone.position == config.end_hub:
        drone.position.drones.pop(drone.id, None)
        drone.active = False

    return {drone.id: drone.position}




def occupy_connection(drone: Drone):
    if isinstance(drone.position, Connection):
        drone.position.drones[drone.id] = drone
        return

    # From current pos to next pos
    for con in drone.next_step.connections:
        if drone.position.name == con.from_zone.name and drone.next_step.name == con.to_zone.name:
            con.drones[drone.id] = drone
            break
        elif drone.position.name == con.to_zone.name and drone.next_step.name == con.from_zone.name:
            con.drones[drone.id] = drone
            break

def clear_connection(drone: Drone):
    if isinstance(drone.position, Connection):
        drone.position.drones.pop(drone.id, None)
        return
    # From current pos to next pos
    for con in drone.next_step.connections:
        if drone.position.name == con.from_zone.name and drone.next_step.name == con.to_zone.name:
            con.drones.pop(drone.id)
            break
        elif drone.position.name == con.to_zone.name and drone.next_step.name == con.from_zone.name:
            con.drones.pop(drone.id)
            break


def move_to_restricted_middle(drone: Drone) -> dict[int, Connection]:
    for con in drone.next_step.connections:
        if con.from_zone.name == drone.position.name and con.to_zone.name == drone.next_step.name:
            # drone.position = con
            drone.on_connection = True
            break
        elif con.to_zone.name == drone.position.name and con.from_zone.name == drone.next_step.name:
            # drone.position = con
            drone.on_connection = True
            break
