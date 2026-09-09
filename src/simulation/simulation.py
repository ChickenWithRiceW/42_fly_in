from src.models import Config, Node, Drone, Connection, NodeType
from .schedular import Schedular
from .helper import SimulationHelper as helper
import heapq


class Simulation:
    @classmethod
    def start(cls,
              config: Config) -> list[dict[int, Node | Connection]] | None:
        """Calculates simulation and returns a list of events

        Args:
            config (Config): Config object with parsed map information

        Returns:
            list[dict[int, Node | Connection]] | None: Returns full action
                log of simulation or none if simulation was not possible
        """
        if not cls._pre_calculate_map(config):
            return None
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
            con = helper._get_connection_to_next_step(
                drone.next_step.connections,
                drone.position,
                drone.next_step
            )
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

    @staticmethod
    def _pre_calculate_map(config: Config) -> bool:
        """Pre calculates map with dijkstra.

        Args:
            config (Config): parsed config object for access to map.

        Returns:
            bool: Returns true when map has a solution and false if not.
        """
        adj = config.nodes
        src = config.end_node.name
        pq: list[tuple[int, str]] = []

        config.end_node.cost = 0
        heapq.heappush(pq, (0, src))

        while pq:
            d, u = heapq.heappop(pq)

            # If this distance not the latest shortest one, skip it
            if d > config.nodes[u].cost:
                continue

            # Explore all neighbors of the current vertex
            for con in adj[u].connections:
                if con.from_node == adj[u]:
                    node = con.to_node
                else:
                    node = con.from_node

                if node.metadata.zone == NodeType.RESTRICTED:
                    w = 2.0
                elif node.metadata.zone == NodeType.BLOCKED:
                    w = float("inf")
                else:
                    w = 1.0

                # If we found a shorter path to v through u, update it
                if config.nodes[u].cost + w < config.nodes[node.name].cost:
                    config.nodes[node.name].cost = config.nodes[u].cost + w
                    heapq.heappush(
                        pq,
                        (config.nodes[node.name].cost, node.name)
                    )

        if config.start_node.cost == float("inf") \
                or config.end_node.metadata.zone == NodeType.BLOCKED:
            print("Error: Map is not solvable")
            return False
        else:
            return True
