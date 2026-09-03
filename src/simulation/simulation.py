from src.models import Config, Hub, Drone, Connection, ZoneType
from dataclasses import dataclass
# Forbid this for now
schedular = {}


@dataclass
class ZoneSelection:
    hub: Hub
    selected: bool


@dataclass
class ZoneOption:
    prio: list[ZoneSelection]
    norm: list[ZoneSelection]


class Schedular:
    def __init__(self):
        self.data: dict[str, ZoneOption] = {}


    def add_zone(self, zone_name: str, list_of_options: list[Hub]) -> None:
        prio: list[ZoneSelection] = list()
        norm: list[ZoneSelection] = list()

        for hub in list_of_options:
            if hub.metadata.zone == ZoneType.PRIORITY:
                prio.append(ZoneSelection(hub, False))
            else:
                norm.append(ZoneSelection(hub, False))

        print("ADDING", len(prio), len(norm))
        options = ZoneOption(prio, norm)

        if self.data.get(zone_name) is None:
            print("INIT")
            self.data[zone_name] = options
        else:
            print("ADDING/REMOVING")
            if not self.data[zone_name].prio:
                print("LIST EMPTY PRIO")
                self.data[zone_name].prio = prio
            else:
                self.data[zone_name].prio = [i for i in prio if i not in self.data[zone_name].prio]

            if not self.data[zone_name].norm:
                print("LIST EMPTY NORM")
                self.data[zone_name].norm = norm
            else:
                print("LIST NORM")
                self.data[zone_name].norm = [i for i in norm if i not in self.data[zone_name].norm]
                print(len(norm))
                print(len(self.data[zone_name].norm))


    def schedular_func(self, zone_name: str) -> Hub:
        print(len(self.data[zone_name].prio), len(self.data[zone_name].norm))
        if self.data[zone_name].prio:
            if not any([d.selected for d in self.data[zone_name].prio]):
                self.data[zone_name].prio[0].selected = True
                return self.data[zone_name].prio[0].hub
            for i, option in enumerate(self.data[zone_name].prio):
                if option.selected:
                    self.data[zone_name].prio[i].selected = False
                    if i == len(self.data[zone_name].prio) - 1:
                        self.data[zone_name].prio[0].selected = True
                        return self.data[zone_name].prio[0].hub
                    else:
                        self.data[zone_name].prio[i + 1].selected = True
                        return self.data[zone_name].prio[i + 1].hub

        if self.data[zone_name].norm:

            if not any([d.selected for d in self.data[zone_name].norm]):
                self.data[zone_name].norm[0].selected = True
                return self.data[zone_name].norm[0].hub

            for i, option in enumerate(self.data[zone_name].norm):
                if option.selected:
                    self.data[zone_name].norm[i].selected = False
                    if i == len(self.data[zone_name].norm) - 1:
                        self.data[zone_name].norm[0].selected = True
                        return self.data[zone_name].norm[0].hub
                    else:
                        self.data[zone_name].norm[i + 1].selected = True
                        return self.data[zone_name].norm[i + 1].hub




    # def schedular_func(self, zone_name: str) -> Hub:
    #     if not any([d[1] for d in schedular[zone_name]]):
    #         schedular[zone_name][0][1] = 1
    #         return schedular[zone_name][0][0]
    #     for i, option in enumerate(schedular[zone_name]):
    #         if option[1] == 1:
    #             schedular[zone_name][i][1] = 0
    #             if i == len(schedular[zone_name]) - 1:
    #                 schedular[zone_name][0][1] = 1
    #                 return schedular[zone_name][0][0]
    #             else:
    #                 schedular[zone_name][i + 1][1] = 1
    #                 return schedular[zone_name][i + 1][0]


def hub_logic(drone: Drone, schedular: Schedular) -> bool:
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
        schedular.add_zone(drone.position.name, lowest_cost_zones)
        drone.next_step = schedular.schedular_func(drone.position.name)
    # print(drone.next_step.name)




def simulation(config: Config) -> list[dict[int, Hub | Connection]]:

    # Max turns before simulation automatically closes itself
    max_run = float("inf")

    # Can maybe be replaced by max run
    simulation_running = True

    drones: list[Drone] = []

    # Populate the drone list.
    for i in range(config.nb_drones):
        drones.append(Drone(id=i, position=config.start_hub, next_step=config.start_hub))

    config.drones = drones

    # Holds information about events.
    action_log = []

    count = 0
    schedular = Schedular()


    while simulation_running:

        max_run -= 1
        round = {}

        if max_run == 0:
            print("LOG: Simulation was closed by max simulation count")
            return action_log

        # All drones reached end goal.
        # TODO: Could be moved to while loop.
        if not drones:
            return action_log

        if count == config.nb_drones:
            return action_log

        # Clear connection occupations of normal connections.
        # TODO: This should not need a clearing like this it would be better to just do it proper. I dont know how yet tho
        for connection in config.connections:
            # if not connection.from_zone.metadata.zone.value == "restricted" and not connection.to_zone.metadata.zone.value == "restricted":
            connection.drones.clear()

        count = 0

        for drone in drones:
            if not drone.active:
                count += 1
                continue

            is_waiting = hub_logic(drone, schedular)

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
                round.update({drone.id: sel_con})

            else:
                drone.on_connection = False
                drone.position = drone.next_step
                round.update({drone.id: drone.position})


            drone.position.drones[drone.id] = drone

            print(drone.id, len(drone.position.drones))

            if isinstance(drone.position, Hub) and drone.position.name == config.end_hub.name:
                drone.position.drones.pop(drone.id)
                drone.active = False

        for connection in config.connections:
            connection.drones.clear()
        if round:
            action_log.append(round)
