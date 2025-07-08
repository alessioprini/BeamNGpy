"""
This example script shows how to use the ``settings.change`` function of the
``BeamNGpy`` class to change graphics settings on startup.
"""

import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..\src')))

from beamngpy import BeamNGpy


def main():
    beamng = BeamNGpy("localhost", 25252, home="C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive")

    with beamng as bng:
        print("Setting BeamNG to fullscreen...")
        bng.settings.change("GraphicDisplayModes", "Fullscreen")
        bng.settings.change("GraphicDisplayResolutions", "1920 1080")
        bng.settings.apply_graphics()

        time.sleep(10)

        print("Setting BeamNG to windowed mode...")
        start_x = 100
        start_y = 100
        width = 1920
        height = 1080
        bng.settings.change("GraphicDisplayModes", "Window")
        bng.settings.change(
            "WindowPlacement",
            f"0 1 -1 -1 -1 -1 {start_x} {start_y} {height + start_y} {width + start_x}",
        )
        bng.settings.apply_graphics()

        input("Press Enter when done...")


if __name__ == "__main__":
    main()
