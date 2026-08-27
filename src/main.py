from .parser import ConfigLoader
from .map.map import idk_yet
from .visual.visual import visual_worker


if __name__ == "__main__":
    config = ConfigLoader.config_loader("example_map.txt")
    if config is None:
        exit()

    idk_yet(config)

    visual_worker(config)