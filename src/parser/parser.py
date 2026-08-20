from pydantic import BaseModel, field_validator, ValidationError, Field
from typing import Optional
from enum import Enum

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    BLACK = "black"
    BROWN = "brown"
    ORANGE = "orange"
    MAROON = "maroon"
    GOLD = "gold"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class HubMetadata(BaseModel):
    color: Optional[Color] = Color.GREEN
    max_drones: Optional[int] = Field(ge=0, default=1)
    zone_type: Optional[ZoneType] = ZoneType.NORMAL


class Hub(BaseModel):
    name: str
    coordinate: tuple[int, int]
    metadata: Optional[HubMetadata] = HubMetadata(
        color=Color.BLUE, zone_type=ZoneType.NORMAL)

    @field_validator('name', mode='after')
    @classmethod
    def _validation(cls, string: str):
        if '-' in string or ' ' in string:
            raise MapException("Name can't contain '-' or ' '")
        return string


class Connection(BaseModel):
    from_zone: str
    to_zone: str
    max_link_capacity: Optional[int] = 1


class MapException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class Map(BaseModel):
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    zones: list[Hub]
    connections: list[Connection]


class ConfigLoader:
    @classmethod
    def config_loader(cls, file_name: str) -> Map | None:
        file = cls._loader(file_name)
        map_val = cls._parser(file)
        return map_val

    @staticmethod
    def _loader(file_name: str) -> list[tuple[list[str], int]] | None:
        """Load config file

        Args:
            file_name (str): Filename of config file

        Returns:
            list[tuple[list[str], int]] | None: List of tuples containing line and line number
        """
        split: list[list[str]] = []

        try:
            with open(file_name) as file:
                for line_nb, line in enumerate(file.readlines(), start=1):
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    split.append((line.split(" ", maxsplit=4), line_nb))
        except FileNotFoundError as e:
            print(f"{e}")
            return None
        return split

    @classmethod
    def _parser(cls, loaded_file: list[list[tuple[str, int]]]):
        nb_drones: int | None = None
        start_hub: Hub = None
        end_hub: Hub = None
        hubs: list[Hub] = []
        connections: list[Connection] = []

        # Index 0 is the key name.
        for line, line_nb in loaded_file:
            match line[0]:
                case "nb_drones:":
                    if nb_drones is not None:
                        print(f"Line:{line_nb} Error: nb_drones was already defined")
                        return False

                    nb_drones = cls._nb_drones_parse(line, line_nb)
                    if nb_drones is None:
                        return False

                case "start_hub:":
                    if start_hub is not None:
                        print(f"Line:{line_nb} Error: start_hub was already defined")
                        return False
                    start_hub = cls._hub_parser(line, line_nb)
                    if start_hub is None:
                        return None

                case "end_hub:":
                    if end_hub is not None:
                        print(f"Line:{line_nb} Error: end_hub was already defined")
                        return False
                    end_hub = cls._hub_parser(line, line_nb)
                    if end_hub is None:
                        return None

                case "hub:":
                    tmp = cls._hub_parser(line, line_nb)
                    if tmp is None:
                        return None
                    hubs.append(tmp)

                case "connection:":
                    tmp = cls._connection_parse(line, line_nb)
                    if tmp is None:
                        return None
                    connections.append(tmp)
                case _:
                    if line[0]:
                        print(f"Line:{line_nb} Error: Unknown keyword '{line[0]}'")
                        return None
        try:
            map_val = Map(
                nb_drones=nb_drones,
                start_hub=start_hub,
                end_hub=end_hub,
                zones=hubs,
                connections=connections
            )

        except ValidationError as e:
            for error in e.errors():
                print(f"Error: Wrong input '{error['input']}'. {error['msg']}")
            return None
        return cls._verify(map_val)

    @staticmethod
    def _nb_drones_parse(input: list[list[str]], line_nb) -> None | int:
        try:
            number = int(input[1])
        except ValueError as e:
            print(f"Line:{line_nb} {e}")
            return None

        if number < 0:
            return None
        return number

    @classmethod
    def _hub_parser(cls, input: list[str], line_nb):
        metadata: HubMetadata = None

        if "-" in input[1]:
            print(f"Line:{line_nb} Error: Can't have '-' in name")
            return None

        if len(input) == 5:
            metadata = cls._hub_metadata_parse(input[4], line_nb)
            if metadata is None:
                return None
        try:
            return Hub(
                name=input[1], coordinate=(input[2], input[3]), metadata=metadata
                )
        except ValidationError as e:
            for error in e.errors():
                print(f"Line:{line_nb} Error: Wrong input '{error['input']}'. {error['msg']}")
            return None


    @classmethod
    def _connection_parse(cls, input: list[str], line_nb: int) -> Connection | None:
        max_link_capacity = {}

        if len(input) > 3:
            print(f"Line:{line_nb} Error: Connection syntax invalid")
            return None
        split = input[1].split('-', maxsplit=3)

        if len(split) < 2:
            print(f"Line:{line_nb} Error: Connection syntax invalid")
            return None

        if len(input) == 3:
            max_link_capacity = cls._metadata_parse(input[2], line_nb)
        try:
            return Connection(from_zone=split[0], to_zone=split[1], **max_link_capacity)
        except ValidationError as e:
            for error in e.errors():
                print(f"Line:{line_nb} Error: Wrong input '{error['input']}'. {error['msg']}")
            return None

    @staticmethod
    def _metadata_parse(input: str, line_nb) -> dict[str, str] | None:
        arguments = {}
        if not input.startswith('[') or not input.endswith(']'):
            print(f"Line:{line_nb} Error: Metadata syntax wrong")
            return None

        input = input.removeprefix('[').removesuffix(']')
        split = input.split(" ", maxsplit=2)

        for data in split:
            # No splitting possible
            if '=' not in data:
                print(f"Line:{line_nb} Error: Format should be: Key=Value")
                return None

            k, v = data.split("=", maxsplit=2)
            arguments[k] = v
        return arguments

    @classmethod
    def _hub_metadata_parse(cls, input: str, line_nb: int) -> HubMetadata | None:
        try:
            return HubMetadata(**cls._metadata_parse(input, line_nb))
        except ValidationError as e:
            for error in e.errors():
                print(f"Line:{line_nb} Error: Wrong input '{error['input']}'. {error['msg']}")
            return None

    @staticmethod
    def _verify(map_val: Map):
        seen = set()

        for hub in map_val.zones:
            if hub.name in seen:
                print(f"Error: Duplicate hub found: '{hub.name}'")
                return None
            else:
                seen.add(hub.name)

        hubs = set(zone.name for zone in map_val.zones)
        hubs.add(map_val.start_hub.name)
        hubs.add(map_val.end_hub.name)

        seen = set()
        for connection in map_val.connections:
            if connection.from_zone not in hubs or connection.to_zone not in hubs:
                print(f"Error: Connection point not found '{connection.from_zone}'")
                return None

            if connection.from_zone == connection.to_zone:
                print(f"Error: Connection can't connect to itself '{connection.from_zone}-{connection.from_zone}'")
                return None

            if (connection.from_zone, connection.to_zone) in seen:
                print(f"Error: Duplicated connection found '{connection.from_zone}-{connection.to_zone}'")
                return None
            else:
                seen.add((connection.from_zone, connection.to_zone))
        return map_val


if __name__ == "__main__":
    map_val = ConfigLoader.config_loader("example_map.txt")

    print(map_val.model_dump_json(indent=2))