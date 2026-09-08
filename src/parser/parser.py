from __future__ import annotations
from src.models import Config, Connection, Node, NodeMetadata
from pydantic import ValidationError
import pygame
from typing import Final, Any

COLOR_URL: Final[str] = "https://www.pygame.org/docs/ref/color_list.html"


class FileData:
    def __init__(
        self,
        file_name: str,
        nodes: dict[str, Node],
        connections: list[Connection]
    ) -> None:

        self.file_name: str = file_name
        self.nodes: dict[str, Node] = nodes
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
        start_node: Node | None = None
        end_node: Node | None = None

        nodes: dict[str, Node] = {}
        connections: list[Connection] = []

        data = FileData(file_name, nodes, connections)

        # Index 0 is the key name.
        for line, line_nb in loaded_file:
            data.line = line
            data.line_nb = line_nb

            match line[0]:
                case "nb_drones:":
                    if not (nb_drones := cls._drone_parser(data, nb_drones)):
                        return None

                case "start_hub:":
                    if not (start_node := cls._hub_parser(data, start_node)):
                        return None
                    nodes.update({start_node.name: start_node})

                case "end_hub:":
                    if not (end_node := cls._hub_parser(
                            data, end_node=end_node)):
                        return None
                    nodes.update({end_node.name: end_node})

                case "hub:":
                    if not (node := cls._hub_parser(data)):
                        return None
                    nodes.update({node.name: node})

                case "connection:":
                    if not (connection := cls._connection_parser(data)):
                        return None

                    cls._connect_hub_to_con(connection, connections, nodes)

                case _:
                    if line[0]:
                        print(
                            f"{file_name}:{line_nb} "
                            f"Error: Unknown key '{line[0]}'")
                        return None

        try:
            return Config(
                nb_drones=nb_drones,
                start_node=start_node,
                end_node=end_node,
                nodes=nodes,
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
        start_node: Node | None = None,
        end_node: Node | None = None
    ) -> Node | None:

        metadata: NodeMetadata | None = NodeMetadata()

        if start_node is not None:
            print(
                f"{data.file_name}:{data.line_nb} "
                "Error: start_hub already defined")
            return None

        if end_node is not None:
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
            hub = Node(
                name=data.line[1],
                pos=pygame.Vector2(int(data.line[2]), int(data.line[3])),
                metadata=metadata
            )

            if hub.name in data.nodes:
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

        if not cls._connection_parser_helper(
                data,
                from_node=split[0],
                to_node=split[1]
        ):
            return None

        try:
            connection = Connection(
                from_node=data.nodes[split[0]],
                to_node=data.nodes[split[1]],
                **max_link_capacity)
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
    ) -> NodeMetadata | None:

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
            return NodeMetadata(**metadata_arguments)
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
    def _connection_parser_helper(
        data: FileData,
        from_node: str,
        to_node: str
    ) -> bool:
        if from_node not in data.nodes \
                or to_node not in data.nodes:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection point not found")
            return False

        if from_node == to_node:
            print(f"{data.file_name}:{data.line_nb} "
                  "Error: Connection can't connect to itself "
                  f"'{from_node}-{from_node}'")
            return False

        for con in data.connections:
            if {from_node, to_node} \
                    == {con.from_node.name, con.to_node.name}:
                print(f"{data.file_name}:{data.line_nb} "
                      "Error: Duplicated connection found "
                      f"'{from_node}-{to_node}'")
                return False
        return True

    @staticmethod
    def _connect_hub_to_con(
        connection: Connection,
        connections: list[Connection],
        hubs: dict[str, Node]
    ) -> None:

        connection.from_node = hubs[connection.from_node.name]
        connection.to_node = hubs[connection.to_node.name]

        connection.from_node.connections.append(connection)
        connection.to_node.connections.append(connection)
        connections.append(connection)
