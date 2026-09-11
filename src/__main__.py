from src.parser import ConfigLoader
from src.visual import Visual
from src.simulation import Simulation
import sys


class App:
    @staticmethod
    def main() -> None:
        if len(sys.argv) != 2:
            print("Usage: python3 -m src <Map_file>")
            return

        if not (config := ConfigLoader.config_loader(sys.argv[1])):
            return

        if config.nb_drones > 999:
            print(f"WARNING: {config.nb_drones} drones, are you sure"
                  " to run the program. This program is not made to handle "
                  "this amount of drones")
            user_choice = input("Y or N: ")
            if user_choice.lower() != "y":
                print("Aborted.")
                return
            print("Good luck.")

        sim = Simulation(config)

        if not sim.solve():
            return

        sim.write_logs_into_file("output.txt")
        Visual.start(config, sim.get_logs())


if __name__ == "__main__":
    App.main()
