from .parser import ConfigLoader
from .map.map import pre_calculate_map
from .visual.visual import visual_worker
from .simulation.simulation import simulation


if __name__ == "__main__":
    config = ConfigLoader.config_loader("example_map.txt")
    if config is None:
        exit()

    pre_calculate_map(config)


    ls = simulation(config)
    print(ls)
    with open("output.log", mode='w') as file:
        for turn in ls:
            for drone in turn:
                print(f"{drone[0]}-{drone[1]} ", end='', file=file)
            print(file=file)

    visual_worker(config, ls)