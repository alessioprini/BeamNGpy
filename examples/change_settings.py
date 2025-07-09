"""
This example script shows how to use the ``settings.change`` function of the
``BeamNGpy`` class to change graphics settings on startup.
"""

import time

from beamngpy import BeamNGpy
from beamngpy import Scenario, Vehicle


def main():
    beamng = BeamNGpy("localhost", 25252, home="C:\\Program Files (x86)\\Steam\\steamapps\\common\\BeamNG.drive")
    beamng.open()
    
    scenario = Scenario("italy", "camera_streaming")

    ego = Vehicle("ego", model="etk800", color="White")
    scenario.add_vehicle(
        ego, pos=(237.90, -894.42, 246.10), rot_quat=(0.0173, -0.0019, -0.6354, 0.7720)
    )

    scenario.make(beamng)

    beamng.settings.set_deterministic(60)

    beamng.control.pause()
    beamng.scenario.load(scenario)
    beamng.scenario.start()



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

    beamng.scenario.stop()
    beamng.close()

if __name__ == "__main__":
    main()
