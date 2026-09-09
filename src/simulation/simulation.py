from src.models import Config, Node, Drone, Connection, NodeType
from .schedular import Schedular
from .helper import SimulationHelper as helper


class Simulation:
    @classmethod
    def start(cls, config: Config) -> list[dict[int, Node | Connection]]:
        drones: list[Drone] = []

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
                cls._transit(drone, schedular, config)

            for drone in drones:
                if not drone.active or drone.is_waiting:
                    continue
                round.update(cls._finalized(drone, config))

            if round:
                action_log.append(round)

        # for connection in config.connections:
        #     connection.drones.clear()
        # for hub in config.nodes.values():
        #     hub.drones.clear()
        return action_log

    @classmethod
    def _transit(
        cls,
        drone: Drone,
        schedular: Schedular,
        config: Config
    ) -> None:
        drone.is_waiting = cls._node_selection(drone, schedular, config)

        if drone.is_waiting:
            return
        if isinstance(drone.position, Node):
            drone.position.drones.pop(drone.id, None)

        helper._occupy_connection(drone)
        drone.next_step.drones[drone.id] = drone

    @classmethod
    def _finalized(
        cls,
        drone: Drone,
        config: Config
    ) -> dict[int, Node | Connection]:
        if isinstance(drone.position, Node) \
                and drone.next_step.metadata.zone == NodeType.RESTRICTED:
            drone.on_connection = True
            con = helper._get_connection_to_next_step(drone.next_step.connections, drone.position, drone.next_step)
            drone.position = con
        else:
            drone.on_connection = False
            helper._clear_connection(drone)
            drone.position = drone.next_step

        if drone.position == config.end_node:
            drone.position.drones.pop(drone.id, None)
            drone.active = False

        return {drone.id: drone.position}

    @classmethod
    def _node_selection(
        cls,
        drone: Drone,
        schedular: Schedular,
        config: Config
    ) -> bool:
        lowest_cost_nodes = []

        if isinstance(drone.position, Connection):
            return False

        lowest_cost_nodes = cls._get_cheapest_available_nodes(drone.position)

        # Could be changed for capacity maxing.
        if not lowest_cost_nodes \
                or drone.position.cost <= lowest_cost_nodes[0].cost:
            return True

        if len(lowest_cost_nodes) == 1:
            drone.next_step = lowest_cost_nodes[0]
        else:
            schedular.add_node(drone.position.name, lowest_cost_nodes)
            drone.next_step = config.nodes[
                schedular.retrieve_node(drone.position.name)]
        return False

    @classmethod
    def _get_cheapest_available_nodes(cls, pos: Node) -> list[Node]:
        lowest_cost_zones: list[Node] = []

        for con in pos.connections:
            zone = helper._get_opposite_zone_of_con(pos, con)

            if len(con.drones) >= con.max_link_capacity:
                continue

            if len(zone.drones) >= zone.metadata.max_drones:
                if zone.metadata.zone != NodeType.RESTRICTED:
                    continue
                if not helper._restricted_zone_access(zone):
                    continue

            if not lowest_cost_zones:
                lowest_cost_zones.append(zone)
            elif zone.cost < lowest_cost_zones[0].cost:
                # If better node was found replace whole list with new node.
                lowest_cost_zones = [zone]
            elif zone.cost == lowest_cost_zones[0].cost:
                # Node found is as good as node before so append to options.
                lowest_cost_zones.append(zone)
        return lowest_cost_zones
