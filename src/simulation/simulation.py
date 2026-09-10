from src.models import Config, Node, Drone, Connection, NodeType
from src.simulation.schedular import Schedular
from src.simulation.helper import SimulationHelper as helper
import heapq


class Simulation:
    def __init__(self, config: Config):
        self._config = config
        self._drones: list[Drone] = []
        self._logs: list[dict[int, Node | Connection]] = []
        self._schedular = Schedular()

    def solve(self) -> bool:
        """Calculates simulation and returns a list of events

        Args:
            config (Config): Config object with parsed map information

        Returns:
            list[dict[int, Node | Connection]] | None: Returns full action
                log of simulation or none if simulation was not possible
        """
        if not self._pre_calculate_map():
            return False
        for i in range(self._config.nb_drones):
            self._drones.append(Drone(
                id=i,
                position=self._config.start_node,
                next_step=self._config.start_node
                )
            )
        self._config.drones = self._drones

        action_log: list[dict[int, Node | Connection]] = []
        count = 0

        while count != self._config.nb_drones:
            count = 0
            round = {}

            for drone in self._drones:
                if not drone.active:
                    count += 1
                    continue
                self._transit(drone)

            for drone in self._drones:
                if not drone.active or drone.is_waiting:
                    continue
                round.update(self._finalized(drone))

            if round:
                action_log.append(round)
        self._logs = action_log
        return True

    def _transit(self, drone: Drone) -> None:
        drone.is_waiting = self._node_selection(drone)

        if drone.is_waiting:
            return
        if isinstance(drone.position, Node):
            drone.position.drones.pop(drone.id, None)

        helper.occupy_connection(drone)
        drone.next_step.drones[drone.id] = drone

    def _finalized(self, drone: Drone) -> dict[int, Node | Connection]:
        assert isinstance(drone.next_step, Node)
        if isinstance(drone.position, Node) \
                and drone.next_step.metadata.zone == NodeType.RESTRICTED:
            drone.on_connection = True
            con = helper.get_connection_to_next_step(
                drone.next_step.connections,
                drone.position,
                drone.next_step
            )
            drone.position = con
        else:
            drone.on_connection = False
            helper.clear_connection(drone)
            drone.position = drone.next_step

        if drone.position == self._config.end_node:
            drone.position.drones.pop(drone.id, None)
            drone.active = False
        return {drone.id: drone.position}

    def _node_selection(self, drone: Drone) -> bool:
        lowest_cost_nodes = []

        if isinstance(drone.position, Connection):
            return False

        lowest_cost_nodes = self._get_cheapest_available_nodes(drone.position)

        # Could be changed for capacity maxing.
        if not lowest_cost_nodes \
                or drone.position.cost <= lowest_cost_nodes[0].cost:
            return True

        if len(lowest_cost_nodes) == 1:
            drone.next_step = lowest_cost_nodes[0]
        else:
            self._schedular._add_node(drone.position.name, lowest_cost_nodes)
            drone.next_step = self._config.nodes[
                self._schedular._retrieve_node(drone.position.name)]
        return False

    @classmethod
    def _get_cheapest_available_nodes(cls, pos: Node) -> list[Node]:
        lowest_cost_zones: list[Node] = []

        for con in pos.connections:
            zone = helper.get_opposite_zone_of_con(pos, con)

            if len(con.drones) >= con.max_link_capacity:
                continue

            if len(zone.drones) >= zone.metadata.max_drones:
                if zone.metadata.zone != NodeType.RESTRICTED:
                    continue
                if not helper.restricted_zone_access(zone):
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

    def write_logs_into_file(self, file_name: str) -> None:
        with open(file_name, mode='w') as file:
            for turn in self._logs:
                if not turn:
                    continue
                turn_list = []
                for id, value in turn.items():
                    if isinstance(value, Connection):
                        turn_list.append(
                            f"D{id + 1} "
                            f"-{value.from_node.name}-{value.to_node.name}")
                    else:
                        turn_list.append(f"D{id + 1}-{value.name}")
                print(*turn_list, file=file)

    def get_logs(self) -> list[dict[int, Node | Connection]]:
        return self._logs

    def _pre_calculate_map(self) -> bool:
        """Pre calculates map with dijkstra.

        Args:
            config (Config): parsed config object for access to map.

        Returns:
            bool: Returns true when map has a solution and false if not.
        """
        adj = self._config.nodes
        src = self._config.end_node.name
        pq: list[tuple[int, str]] = []

        self._config.end_node.cost = 0
        heapq.heappush(pq, (0, src))

        while pq:
            d, u = heapq.heappop(pq)

            if d > self._config.nodes[u].cost:
                continue

            for con in adj[u].connections:
                self._explore_neighbor(con, adj, u, pq)

        if self._config.start_node.cost == float("inf") \
                or self._config.end_node.metadata.zone == NodeType.BLOCKED:
            print("Error: Map is not solvable")
            return False
        else:
            return True

    def _explore_neighbor(self, con: Connection, adj: dict[str, Node],
                          u: str, pq: list[tuple[int, str]]) -> None:
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
        if self._config.nodes[u].cost + w < self._config.nodes[node.name].cost:
            self._config.nodes[node.name].cost = self._config.nodes[u].cost + w

            heapq.heappush(
                pq,
                (int(self._config.nodes[node.name].cost), node.name)
            )
