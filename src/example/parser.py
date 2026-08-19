from pydantic import BaseModel, field_validator
from typing import Optional
from enum import IntEnum


class Color(IntEnum):
    RED = 0
    GREEN = 1
    BLUE = 2


class ZoneType(IntEnum):
    NORMAL = 0
    RESTRICTED = 1
    PRIORITY = 2
    BLOCKED = 3


class HubMetadata:
    def __init__(self, color: Color, zone_type: ZoneType):
        self.color = color
        self.zone_type = zone_type


class ConnectionMetadata:
    def __init__(self, color: Color, zone_type: ZoneType):
        self.color = color
        self.zone_type = zone_type


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    metadata: Optional[HubMetadata] = HubMetadata(Color.BLUE, ZoneType.NORMAL)

    @field_validator('name', mode='after')
    @classmethod
    def _validation(cls, string: str):
        if '-' in string or ' ' in string:
            return False
        return True


class Connection(BaseModel):
    from_zone: Hub
    to_zone: Hub
    max_link_capacity: Optional[int] = 1


class Map(BaseModel):
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    zones: list[Hub]
    connections: list[Connection]


def loader(file_name: str):
    split: list[str] = []

    try:
        with open(file_name) as file:
            for line in file.readlines():
                # Remove trailing whitespaces.
                line = line.strip()
                if line.startswith('#'):
                    continue
                split = line.split(" ")


    except FileNotFoundError as e:
        print(f"{e}")
        return


if __name__ == "__main__":
    loader("example.txt")