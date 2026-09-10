from dataclasses import dataclass
from src.models import Node, NodeType


@dataclass
class ZoneOption:
    prio: dict[str, bool]
    norm: dict[str, bool]


class Schedular:
    def __init__(self) -> None:
        self._data: dict[str, ZoneOption] = {}

    def _insert_nodes(
        self,
        selected_queue: dict[str, bool],
        queue_type: dict[str, bool]
    ) -> None:
        if not selected_queue:
            selected_queue = queue_type
        else:
            for key, value in selected_queue.items():
                if key not in queue_type.keys():
                    continue
                queue_type[key] = value
            selected_queue = queue_type

    def _inserting_prio_norm_nodes(
        self,
        zone_name: str,
        options: ZoneOption
    ) -> None:
        self._insert_nodes(self._data[zone_name].prio, options.prio)
        self._insert_nodes(self._data[zone_name].norm, options.norm)

    def _add_node(self, zone_name: str, list_of_options: list[Node]) -> None:
        prio = {}
        norm = {}

        for hub in list_of_options:
            if hub.metadata.zone == NodeType.PRIORITY:
                prio[hub.name] = False
            else:
                norm[hub.name] = False

        options = ZoneOption(prio, norm)

        if self._data.get(zone_name) is None:
            self._data[zone_name] = options
        else:
            self._inserting_prio_norm_nodes(zone_name, options)

    def _retrieve_node(self, zone_name: str) -> str:
        if self._data[zone_name].prio:
            return self._get_selected_node(self._data[zone_name].prio)
        return self._get_selected_node(self._data[zone_name].norm)

    def _get_node(self, zone_name: str, list_of_options: list[Node]) -> str:
        self._add_node(zone_name, list_of_options)
        return self._retrieve_node(zone_name)

    def _get_selected_node(self, selected_zone_type: dict[str, bool]) -> str:
        if not any(list(selected_zone_type.values())):
            node_name: str = list(selected_zone_type.keys())[0]
            selected_zone_type[node_name] = True
            return node_name

        tmp: list[str] = list(selected_zone_type.keys())
        for i, node_name in enumerate(tmp):
            if selected_zone_type[node_name]:
                selected_zone_type[node_name] = False

                if i == len(selected_zone_type) - 1:
                    selected_zone_type[tmp[0]] = True
                    return tmp[0]
                else:
                    selected_zone_type[tmp[i + 1]] = True
                    return tmp[i + 1]
        raise Exception("Shouldn't happen (Mypy is happy now)")
