from dataclasses import dataclass
from src.models import Node, NodeType


@dataclass
class ZoneOption:
    prio: dict
    norm: dict


class Schedular:
    def __init__(self):
        self.data: dict[str, ZoneOption] = {}

    def _proper_thing(self, selected_queue: dict, queue_type: dict):
        if not selected_queue:
            selected_queue = queue_type
        else:
            for key, value in selected_queue.items():
                if key not in queue_type.keys():
                    continue
                queue_type[key] = value

            selected_queue = queue_type


    def _adding_thing(self, zone_name: str, options: ZoneOption):
        self._proper_thing(self.data[zone_name].prio, options.prio)

        self._proper_thing(self.data[zone_name].norm, options.norm)

    def add_node(self, zone_name: str, list_of_options: list[Node]):
        prio = {}
        norm = {}

        for hub in list_of_options:
            if hub.metadata.zone == NodeType.PRIORITY:
                prio[hub.name] = False
            else:
                norm[hub.name] = False

        options = ZoneOption(prio, norm)

        if self.data.get(zone_name) is None:
            self.data[zone_name] = options
        else:
            _adding_thing(zone_name, options)



    def retrieve_node(self, zone_name: str) -> Node:
        print(len(self.data[zone_name].prio), len(self.data[zone_name].norm))


        if self.data[zone_name].prio:
            if not any(list(self.data[zone_name].prio.values())):
                key = list(self.data[zone_name].prio.keys())[0]
                self.data[zone_name].prio[key] = True
                return key

            tmp = list(self.data[zone_name].prio.keys())
            for i, key in enumerate(tmp):
                if self.data[zone_name].prio[key]:
                    self.data[zone_name].prio[key] = False

                    if i == len(self.data[zone_name].prio) - 1:
                        self.data[zone_name].prio[tmp[0]] = True
                        return tmp[0]
                    else:
                        self.data[zone_name].prio[tmp[i + 1]] = True
                        return tmp[i + 1]

        if self.data[zone_name].norm:
            if not any(list(self.data[zone_name].norm.values())):
                key = list(self.data[zone_name].norm.keys())[0]
                self.data[zone_name].norm[key] = True
                return key

            tmp = list(self.data[zone_name].norm.keys())
            for i, key in enumerate(tmp):
                if self.data[zone_name].norm[key]:
                    self.data[zone_name].norm[key] = False

                    if i == len(self.data[zone_name].norm) - 1:
                        self.data[zone_name].norm[tmp[0]] = True
                        return tmp[0]
                    else:
                        self.data[zone_name].norm[tmp[i + 1]] = True
                        return tmp[i + 1]

    def get_node(self, zone_name: str, list_of_options: list[Node]) -> Node:
        self.add_node(zone_name, list_of_options)
        return self.retrieve_node(zone_name)
