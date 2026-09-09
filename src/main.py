from src.parser import ConfigLoader
from src.models import Connection
from .visual.visual import visual_worker
from .simulation.simulation import Simulation
import sys


class App:
    @staticmethod
    def main():
        if len(sys.argv) != 2:
            print("Usage: ./fly_in <Map_file>")
            return

        if not (config := ConfigLoader.config_loader(sys.argv[1])):
            return

        ls = Simulation.start(config)

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


if __name__ == "__main__":
    App.main()
