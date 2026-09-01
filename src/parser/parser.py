from __future__ import annotations
from pydantic import ValidationError
from ..parser.config import Config, Connection, Hub, HubMetadata
import pygame
from typing import Final, Any

COLOR_URL: Final[str] = "https://www.pygame.org/docs/ref/color_list.html"


class FileData:
    def __init__(
        self,
        file_name: str,
        hubs: dict[str, Hub],
        connections: list[Connection]
    ) -> None:

        self.file_name: str = file_name
        self.hubs: dict[str, Hub] = hubs
        self.connections: list[Connection] = connections
        self.line: list[str]
        self.line_nb: int


class ConfigLoader:
    @classmethod
    def config_loader(cls, file_name: str) -> Config | None:
        """Load config from provided file name if possible.
        Checks for errors prints them and returns None if failed

        Args:
            file_name (str): Filename of config file

        Returns:
            Config | None: Config object or None if loading did not work.
        """
        if (file := cls._loader(file_name)) is None:
            return None
        if (config := cls._parser(file, file_name)) is None:
            return None

        return config

    @staticmethod
    def _loader(file_name: str) -> list[tuple[list[str], int]] | None:
        """Load config file

        Args:
            file_name (str): Filename of config file

        Returns:
            list[tuple[list[str], int]] | None: List of tuples containing line
                and line number
        """
        split: list[tuple[list[str], int]] = []

        try:
            with open(file_name) as file:
                for line_nb, line in enumerate(file.readlines(), start=1):
                    line = line.strip()
                    # Skip comments
                    if line.startswith('#'):
                        continue
                    split.append((line.split(" ", maxsplit=4), line_nb))
        except FileNotFoundError as e:
            print(f"{e}")
            return None
        return split

    @classmethod
    def _parser(
        cls,
        loaded_file: list[tuple[list[str], int]],
        file_name: str
    ) -> Config | None:
        """Parse given list of tuples to check for malformed lines etc.

        Args:
            loaded_file (list[tuple[list[str], int]]): Read file from
                config_loader
            file_name (str): Config filename

        Returns:
            Config | None: Returns either config object or None if errors
                occurred
        """
        nb_drones: int | None = None
        start_hub: Hub | None = None
        end_hub: Hub | None = None

        hubs: dict[str, Hub] = {}
        connections: list[Connection] = []

        data = FileData(file_name, hubs, connections)

        # Index 0 is the key name.
        for line, line_nb in loaded_file:
            data.line = line
            data.line_nb = line_nb

            match line[0]:
                case "nb_drones:":
                    if not (nb_drones := cls._drone_parser(data, nb_drones)):
                        return None

                case "start_hub:":
                    if not (start_hub := cls._hub_parser(data, start_hub)):
                        return None
                    hubs.update({start_hub.name: start_hub})

                case "end_hub:":
                    if not (end_hub := cls._hub_parser(data, end_hub=end_hub)):
                        return None
                    hubs.update({end_hub.name: end_hub})

                case "hub:":
                    if not (hub := cls._hub_parser(data)):
                        return None
                    hubs.update({hub.name: hub})

                case "connection:":
                    if not (connection := cls._connection_parser(data)):
                        return None

                    cls._connect_hub_to_con(connection, connections, hubs)

                case _:
                    if line[0]:
                        print(
                            f"{file_name}:{line_nb} "
                            f"Error: Unknown key '{line[0]}'")
                        return None

        try:
            return Config(
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

    @staticmethod
    def _drone_parser(data: FileData, nb_drones: int | None) -> None | int:
        if nb_drones is not None:
            print(
                f"{data.file_name}:{data.line_nb} "
                "Error: nb_drones already defined")
            return None

        try:
            number = int(data.line[1])
        except ValueError as e:
            print(f"{data.file_name}:{data.line_nb} {e}")
            return None

        if number < 1:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: nb_drones needs to a positive integer")
            return None
        return number

    @classmethod
    def _hub_parser(
        cls,
        data: FileData,
        start_hub: Hub | None = None,
        end_hub: Hub | None = None
    ) -> Hub | None:

        metadata: HubMetadata | None = HubMetadata()

        if start_hub is not None:
            print(
                f"{data.file_name}:{data.line_nb} "
                "Error: start_hub already defined")
            return None

        if end_hub is not None:
            print(
                f"{data.file_name}:{data.line_nb} "
                "Error: end_hub already defined")
            return None

        if "-" in data.line[1]:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Can't have '-' in name")
            return None

        if len(data.line) == 5:
            metadata = cls._hub_metadata_parse(data)
            if metadata is None:
                return None
        try:
            hub = Hub(
                name=data.line[1],
                coordinate=(data.line[2], data.line[3]),
                metadata=metadata
            )

            if hub.name in data.hubs:
                print(f"{data.file_name}:{data.line_nb} "
                      "Error: Zone duplicate found")
                return None
            return hub
        except ValidationError as e:
            for error in e.errors():
                print(f"{data.file_name}:{data.line_nb} "
                      f"Error: Wrong input '{error['input']}'. {error['msg']}")
            return None

    @classmethod
    def _connection_parser(cls, data: FileData) -> Connection | None:

        max_link_capacity: dict[str, str] | None = {}

        if len(data.line) > 3:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection syntax invalid")
            return None
        split = data.line[1].split('-', maxsplit=3)

        if len(split) < 2:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection syntax invalid")
            return None

        if len(data.line) == 3:
            max_link_capacity = cls._metadata_parse(data, data.line[2])
        if max_link_capacity is None:
            return None
        try:
            connection = Connection(
                from_zone=split[0],
                to_zone=split[1],
                **max_link_capacity)

            if not cls._connection_parser_helper(data, connection):
                return None

            return connection

        except ValidationError as e:
            for error in e.errors():
                print(f"{data.file_name}:{data.line_nb} "
                      "Error: Wrong input "
                      f"'{error['input']}'. {error['msg']}")
            return None

    @staticmethod
    def _metadata_parse(data: FileData, input: str) -> dict[str, Any] | None:
        arguments = {}

        if not input.startswith('[') or not input.endswith(']'):
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Metadata syntax wrong")
            return None

        input = input.removeprefix('[').removesuffix(']')
        split = input.split(" ", maxsplit=2)

        for part in split:
            # No splitting possible
            if '=' not in part:
                print(f"{data.file_name}:{data.line_nb} "
                      "Error: Format should be: Key=Value")
                return None

            key, value = part.split("=", maxsplit=2)
            arguments[key] = value
        return arguments

    @classmethod
    def _hub_metadata_parse(
        cls,
        data: FileData
    ) -> HubMetadata | None:

        metadata_arguments: dict[str, Any] | None

        metadata_arguments = cls._metadata_parse(data, data.line[4])
        if metadata_arguments is None:
            return None
        try:
            if (selc := metadata_arguments.get("color")) is not None:
                if metadata_arguments["color"] in pygame.color.THECOLORS:
                    metadata_arguments["color"] = pygame.color.THECOLORS[selc]
                else:
                    print(f"{data.file_name}:{data.line_nb} "
                          "Error: Color not supported. "
                          f"Supported colors: {COLOR_URL}")
                    return None
            return HubMetadata(**metadata_arguments)
        except ValidationError as e:
            for error in e.errors():
                if error["type"] == "extra_forbidden":
                    print(f"{data.file_name}:{data.line_nb} "
                          "Error: Metadata keyword no match "
                          f"'{error["loc"][0]}'")
                else:
                    print(f"{data.file_name}:{data.line_nb} "
                          "Error: Wrong input "
                          f"{error["loc"][0]} = '{error['input']}'. "
                          f"{error['msg']}")
            return None

    @staticmethod
    def _connection_parser_helper(data: FileData, sel: Connection) -> bool:
        if sel.from_zone not in data.hubs \
                or sel.to_zone not in data.hubs:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection point not found")
            return False

        if sel.from_zone == sel.to_zone:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection can't connect to itself "
                  f"'{sel.from_zone}-{sel.from_zone}'")
            return False

        for con in data.connections:
            if {sel.from_zone, sel.to_zone} \
                    == {con.from_zone.name, con.to_zone.name}:
                print(f"{data.file_name}:{data.line_nb} "
                      "Error: Duplicated connection found "
                      f"'{sel.from_zone}-{sel.to_zone}'")
                return False
        return True

    @staticmethod
    def _connect_hub_to_con(
        connection: Connection,
        connections: list[Connection],
        hubs: dict[str, Hub]
    ) -> None:

        connection.from_zone = hubs[connection.from_zone]
        connection.to_zone = hubs[connection.to_zone]

        connection.from_zone.connections.append(connection)
        connection.to_zone.connections.append(connection)
        connections.append(connection)
