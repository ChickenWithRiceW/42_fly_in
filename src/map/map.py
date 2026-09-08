from src.models import Config, NodeType
import heapq


def pre_calculate_map(config: Config) -> bool:
    """Pre calculates map with dijkstra.

    Args:
        config (Config): parsed config object for access to map.

    Returns:
        bool: Returns true when map has a solution and false if not.
    """
    adj = config.nodes

    src = config.end_node.name

    # Min-heap (priority queue) storing pairs of (distance, node)
    pq: list[tuple[int, str]] = []

    # Distance from source to itself is 0
    config.end_node.cost = 0
    heapq.heappush(pq, (0, src))

    # Process the queue until all reachable vertices are finalized
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
                heapq.heappush(pq, (config.nodes[node.name].cost, node.name))

    if config.start_node.cost == float("inf") \
            or config.end_node.metadata.zone == NodeType.BLOCKED:
        print("Error: Map is not solvable")
        return False
    else:
        return True
