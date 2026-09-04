from dataclasses import dataclass
from src.models import Hub, ZoneType


@dataclass
class ZoneOption:
    prio: dict
    norm: dict


class Schedular:
    def __init__(self):
        self.data: dict[str, ZoneOption] = {}


    def add_zone(self, zone_name: str, list_of_options: list[Hub]):
        prio = {}
        norm = {}

        for hub in list_of_options:
            if hub.metadata.zone == ZoneType.PRIORITY:
                prio[hub.name] = False
            else:
                norm[hub.name] = False

        print("ADDING", len(prio), len(norm))
        options = ZoneOption(prio, norm)

        if self.data.get(zone_name) is None:
            print("INIT")
            self.data[zone_name] = options
        else:
            print("ADDING/REMOVING")
            if not self.data[zone_name].prio:
                print("LIST EMPTY PRIO")
                self.data[zone_name].prio = prio
            else:
                for key, value in self.data[zone_name].prio.items():
                    if key not in prio.keys():
                        continue
                    prio[key] = value

                self.data[zone_name].prio = prio

            if not self.data[zone_name].norm:
                print("LIST EMPTY NORM")
                self.data[zone_name].norm = norm
            else:
                for key, value in self.data[zone_name].norm.items():
                    if key not in norm.keys():
                        continue
                    norm[key] = value

                self.data[zone_name].norm = norm



    def schedular_func(self, zone_name: str) -> Hub:
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
