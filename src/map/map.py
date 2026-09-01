from ..parser.config import ZoneType, Config
import heapq


def pre_calculate_map(config: Config) -> bool:
    """Pre calculates map with dijkstra.

    Args:
        config (Config): parsed config object for access to map.

    Returns:
        bool: Returns true when map has a solution and false if not.
    """
    adj = config.zones

    src = config.end_hub.name

    # Min-heap (priority queue) storing pairs of (distance, node)
    pq: list[tuple[int, str]] = []

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

            if hub.metadata.zone == ZoneType.RESTRICTED:
                w = 2.0
            elif hub.metadata.zone == ZoneType.BLOCKED:
                w = float("inf")
            else:
                w = 1.0

            # If we found a shorter path to v through u, update it
            if config.zones[u].cost + w < config.zones[hub.name].cost:
                config.zones[hub.name].cost = config.zones[u].cost + w
                heapq.heappush(pq, (config.zones[hub.name].cost, hub.name))

    if config.start_hub.cost == float("inf") \
            or config.end_hub.metadata.zone == ZoneType.BLOCKED:
        print("Error: Map is not solvable")
        return False
    else:
        return True
