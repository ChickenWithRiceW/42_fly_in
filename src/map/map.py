from __future__ import annotations
from ..parser.parser import Hub, HubMetadata, Config
from ..parser.config import Direction, ZoneType
import heapq
import sys


class Zone:
    def __init__(
            self,
            name: str,
            metadata: HubMetadata):
        self.name = name
        self.connections = []
        self.metadata = metadata


class Connection:
    def __init__(
            self,
            name: str,
            from_zone: Zone,
            to_zone: Zone,
            direction: Direction,
            max_link_capacity: int):

        self.name = name
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.direction = Direction

        self.max_link_capacity = max_link_capacity
        self.step_cost_to_end: list[int] = []


class Drone:
    def __init__(self, id: int):
        self.id = id
        self.next_step: Hub
        self.position: tuple[int, int]


def idk_yet(config: Config) -> None:

    # Linking the zones in the connections.
    for connection in config.connections:
        connection.from_zone = config.zones[connection.from_zone]
        connection.to_zone = config.zones[connection.to_zone]

        connection.from_zone.connections.append(connection)
        connection.to_zone.connections.append(connection)

    start = config.end_hub

    for connection in start.connections:
        if connection.to_zone != start:
            to_zone = connection.to_zone
            connection.to_zone = connection.from_zone
            connection.from_zone = to_zone

    zone_list = []
    list_idk = [config.end_hub]

    cost = 0

    seen = []

    while list_idk:

        zone_list = list_idk.copy()

        print(len(zone_list))
        # Go trough the zones.

        for zone in zone_list:
            print(list_idk.pop(0).name)
            print("After pop", len(list_idk))


            # Check all of the connections of selected zone.
            for connection in zone.connections:

                state = False
                direction_tmp = Direction.MONO

                seen.append(connection)
                # Skip connection that was already handled.
                if connection.direction != Direction.NONE:
                    continue

                # Setting the correct direction
                if connection.to_zone != zone:
                    to_zone = connection.to_zone
                    connection.to_zone = connection.from_zone
                    connection.from_zone = to_zone

                for con in connection.from_zone.connections:
                    if con.direction != Direction.NONE:
                        direction_tmp = Direction.BI
                        if con not in seen:
                            # state = False
                            continue
                        break
                    
                connection.direction = direction_tmp
                if not state:
                    list_idk.append(connection.from_zone)

    dijkstra(config)
    


def dijkstra(config: Config):
    adj = config.zones

    # print(adj[0].name)
    # for t in test:
    #     print(t.name)
    # V = len(adj)

    src = config.end_hub.name

    # Min-heap (priority queue) storing pairs of (distance, node)
    pq = []

    dist = {key: float("inf") for key in config.zones.keys()}

    # Distance from source to itself is 0
    dist[src] = 0
    heapq.heappush(pq, (0, src))

    # Process the queue until all reachable vertices are finalized
    while pq:
        d, u = heapq.heappop(pq)

        # If this distance not the latest shortest one, skip it
        if d > dist[u]:
            continue

        # Explore all neighbors of the current vertex
        for con in adj[u].connections:
            if con.from_zone == adj[u]:
                hub = con.to_zone
            else:
                hub = con.from_zone

            if hub.metadata.zone == ZoneType.NORMAL:
                w = 1
            elif hub.metadata.zone == ZoneType.RESTRICTED:
                w = 2
            elif hub.metadata.zone == ZoneType.PRIORITY:
                w = 0.5

            elif hub.metadata.zone == ZoneType.BLOCKED:
                w = float("inf")

            # If we found a shorter path to v through u, update it
            if dist[u] + w < dist[hub.name]:
                dist[hub.name] = dist[u] + w
                heapq.heappush(pq, (dist[hub.name], hub.name))


    print(dist["gate_hell3"])
    # Return the final shortest distances from the source
    return dist


def dijkstra(config: Config):
    adj = config.zones

    # print(adj[0].name)
    # for t in test:
    #     print(t.name)
    # V = len(adj)

    src = config.end_hub.name

    # Min-heap (priority queue) storing pairs of (distance, node)
    pq = []

    # dist = {key: float("inf") for key in config.zones.keys()}

    # Distance from source to itself is 0
    config.end_hub.cost = 0
    heapq.heappush(pq, (0, src))

    # Process the queue until all reachable vertices are finalized
    while pq:
        d, u = heapq.heappop(pq)

        # If this distance not the latest shortest one, skip it
        if d > config.zones[u].cost:
            continue

        # Explore all neighbors of the current vertex
        for con in adj[u].connections:
            if con.from_zone == adj[u]:
                hub = con.to_zone
            else:
                hub = con.from_zone

            if hub.metadata.zone == ZoneType.NORMAL:
                w = 1
            elif hub.metadata.zone == ZoneType.RESTRICTED:
                w = 2
            elif hub.metadata.zone == ZoneType.PRIORITY:
                w = 0.5

            elif hub.metadata.zone == ZoneType.BLOCKED:
                w = float("inf")

            # If we found a shorter path to v through u, update it
            if config.zones[u].cost + w < config.zones[hub.name].cost:
                config.zones[hub.name].cost = config.zones[u].cost + w
                heapq.heappush(pq, (config.zones[hub.name].cost, hub.name))


    print(config.zones["gate_hell3"].cost)
    # Return the final shortest distances from the source
    # return config.zones