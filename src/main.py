from .parser import ConfigLoader
from src.models import Connection
from .map.map import pre_calculate_map
from .visual.visual import visual_worker
from .simulation.simulation import simulation


if __name__ == "__main__":
    config = ConfigLoader.config_loader("example_map.txt")
    if config is None:
        exit()

    pre_calculate_map(config)


    ls = simulation(config)

    with open("output.log", mode='w') as file:
        for turn in ls:
            if not turn:
                continue
            turn_list = []
            for id, value in turn.items():
                if isinstance(value, Connection):
                    turn_list.append(f"D{id + 1}-{value.from_node.name}-{value.to_node.name}")
                else:
                    turn_list.append(f"D{id + 1}-{value.name}")
            print(*turn_list, file=file)

    visual_worker(config, ls)