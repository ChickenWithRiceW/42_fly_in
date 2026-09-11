from src.models import Node, Connection, Drone


class SimulationHelper:
    @classmethod
    def restricted_zone_access(cls, zone: Node) -> bool:
        moveable_drones = 0
        used_capacity = len(zone.drones)

        for o_drone in zone.drones.values():
            if o_drone.on_connection or o_drone.is_waiting:
                moveable_drones += 1

        max_moveable_drones = cls._get_max_moveable_drones(zone)
        moving_drones = min(max_moveable_drones, moveable_drones)

        if 1 + (used_capacity - moving_drones) <= zone.metadata.max_drones:
            return True
        return False

    @staticmethod
    def get_opposite_zone_of_con(node: Node, con: Connection) -> Node:
        if con.from_node.name == node.name:
            return con.to_node
        else:
            return con.from_node

    @classmethod
    def _get_max_moveable_drones(cls, node: Node) -> int:
        max_move = 0

        for con in node.connections:
            o_zone = cls.get_opposite_zone_of_con(node, con)

            if o_zone.cost < node.cost:
                max_move += min(
                    (con.max_link_capacity - len(con.drones),
                        (o_zone.metadata.max_drones - len(o_zone.drones)))
                )
        return max_move

    @classmethod
    def occupy_connection(cls, drone: Drone) -> None:
        if isinstance(drone.position, Connection):
            drone.position.drones[drone.id] = drone
        else:
            assert isinstance(drone.next_step, Node)
            con = cls.get_connection_to_next_step(
                drone.position, drone.next_step)
            con.drones[drone.id] = drone

    @classmethod
    def clear_connection(cls, drone: Drone) -> None:
        if isinstance(drone.position, Connection):
            drone.position.drones.pop(drone.id, None)
        else:
            con = cls.get_connection_to_next_step(
                drone.position, drone.next_step)
            con.drones.pop(drone.id, None)

    @staticmethod
    def get_connection_to_next_step(
            a: Node | Connection, b: Node | Connection) -> Connection:
        if isinstance(a, Node):
            connections = a.connections
        else:
            return a
        if isinstance(b, Node):
            connections = b.connections
        else:
            return b

        for con in connections:
            if a == con.from_node \
                    and b == con.to_node:
                break
            elif a == con.to_node \
                    and b == con.from_node:
                break
        return con
