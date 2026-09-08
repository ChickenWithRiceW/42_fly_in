from src.models import Config, Node, Drone, Connection, NodeType
from .schedular import Schedular
from .helper import _get_opposite_zone_of_con, _get_max_moveable_drones


class Simulation:
    @staticmethod
    def start(config: Config) -> list[dict[int, Node | Connection]]:
        drones: list[Drone] = []

        # Populate the drone list.
        for i in range(config.nb_drones):
            drones.append(Drone(
                id=i,
                position=config.start_node,
                next_step=config.start_node
                )
            )
        config.drones = drones

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
                if not drone.active or drone.is_waiting:
                    continue
                round.update(finalized(drone, config))

            action_log.append(round)


        for connection in config.connections:
            connection.drones.clear()
        for hub in config.nodes.values():
            hub.drones.clear()
        return action_log


    def _get_cheapest_available_nodes(drone: Drone) -> list[Node]:
        lowest_cost_zones = []

        for con in drone.position.connections:
            zone = _get_opposite_zone_of_con(drone.position, con)

            if len(con.drones) >= con.max_link_capacity:
                continue

            if len(zone.drones) >= zone.metadata.max_drones:
                if zone.metadata.zone != NodeType.RESTRICTED:
                    continue
                if not restricted_zone_access(zone):
                    continue

            if not lowest_cost_zones:
                lowest_cost_zones.append(zone)
            elif zone.cost < lowest_cost_zones[0].cost:
                lowest_cost_zones = [zone]
            elif zone.cost == lowest_cost_zones[0].cost:
                lowest_cost_zones.append(zone)

        return lowest_cost_zones


    def _restricted_zone_access(zone: Node) -> bool:
        moveable_drones = 0
        used_capacity = len(zone.drones)

        for o_drone in zone.drones.values():
            if o_drone.on_connection or o_drone.is_waiting:
                moveable_drones += 1

        max_moveable_drones = _get_max_moveable_drones(zone)
        moving_drones = min(max_moveable_drones, moveable_drones)

        if 1 + (used_capacity - moving_drones) <= zone.metadata.max_drones:
            return True
        return False


    def _node_selection(drone: Drone, schedular: Schedular, config: Config) -> bool:
        lowest_cost_nodes = []

        if isinstance(drone.position, Connection):
            return False

        lowest_cost_nodes = _get_cheapest_available_nodes(drone)

        # Could be changed for capacity maxing.
        if not lowest_cost_nodes or drone.position.cost <= lowest_cost_nodes[0].cost:
            return True

        if len(lowest_cost_nodes) == 1:
            drone.next_step = lowest_cost_nodes[0]
        else:
            schedular.add_node(drone.position.name, lowest_cost_nodes)
            drone.next_step = config.nodes[schedular.retrieve_node(drone.position.name)]
        return False


    def _transit(drone: Drone, schedular, config) -> bool:
        drone.is_waiting = node_selection(drone, schedular, config)

        if drone.is_waiting:
            return

        # Remove occupation of zone before.
        if isinstance(drone.position, Node):
            drone.position.drones.pop(drone.id, None)

        # This will occupy the connection between current pos and next pos
        occupy_connection(drone)

        drone.next_step.drones[drone.id] = drone


    def _finalized(drone: Drone, config: Config) -> dict[int, Node | Connection]:
        if isinstance(drone.position, Node) and drone.next_step.metadata.zone == NodeType.RESTRICTED:
            drone.on_connection = True
            con = get_connection_to_next_step(drone)

            drone.position = con
        else:
            drone.on_connection = False
            clear_connection(drone)
            drone.position = drone.next_step

        # If reached goal drone deactivates.
        if drone.position == config.end_node:
            drone.position.drones.pop(drone.id, None)
            drone.active = False

        return {drone.id: drone.position}


    def _occupy_connection(drone: Drone):
        if isinstance(drone.position, Connection):
            drone.position.drones[drone.id] = drone
            return

        # From current pos to next pos
        con = get_connection_to_next_step(drone)
        con.drones[drone.id] = drone


    def _clear_connection(drone: Drone):
        if isinstance(drone.position, Connection):
            drone.position.drones.pop(drone.id, None)
            return
        # From current pos to next pos
        con = get_connection_to_next_step(drone)
        con.drones.pop(drone.id)


    def _get_connection_to_next_step(drone: Drone) -> None:
        for con in drone.next_step.connections:
            if drone.position.name == con.from_node.name \
                    and drone.next_step.name == con.to_node.name:
                return con
            elif drone.position.name == con.to_node.name \
                    and drone.next_step.name == con.from_node.name:
                return con
