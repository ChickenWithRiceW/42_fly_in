from src.parser import ConfigLoader
from src.visual import Visual
from src.simulation import Simulation
import sys


class App:
    @staticmethod
    def main() -> None:
        if len(sys.argv) != 2:
            print("Usage: ./fly_in <Map_file>")
            return

        if not (config := ConfigLoader.config_loader(sys.argv[1])):
            return

        sim = Simulation(config)

        if not sim.solve():
            return

        sim.write_logs_into_file("output.txt")
        Visual.start(config, sim.get_logs())


if __name__ == "__main__":
    App.main()
