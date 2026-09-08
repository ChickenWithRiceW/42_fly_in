from src.models import Node, Connection


def _get_opposite_zone_of_con(node: Node, con: Connection) -> Node:
    if con.from_node.name == node.name:
        return con.to_node
    else:
        return con.from_node


def _get_max_moveable_drones(node: Node):
    max_move = 0

    for con in node.connections:
        o_zone = _get_opposite_zone_of_con(node, con)

        if o_zone.cost < node.cost:
            max_move += min(
                (con.max_link_capacity - len(con.drones),
                    (o_zone.metadata.max_drones - len(o_zone.drones)))
            )

    return max_move
