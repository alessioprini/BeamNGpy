"""
This example script shows how to use the ``settings.change`` function of the
``BeamNGpy`` class to change graphics settings on startup.
"""

import time

from beamngpy import BeamNGpy
from beamngpy import Scenario, Vehicle
import subprocess
import os

# ['C:\\Program Files (x86)\\Steam\\steamapps\\common\\BeamNG.drive\\Bin64\\BeamNG.drive.x64.exe', '-nosteam', '-console', '-tcom-listen-ip', '127.0.0.1', '-lua', "extensions.load('tech/techCore');tech_techCore.openServer(25252)", '-userpath', 'C:\\Users\\AlessioPrini\\AppData\\Local\\BeamNG.drive']

def main():
    beamng_dir = "C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive"
    beamng_path = os.path.join(beamng_dir, "Bin64", "BeamNG.drive.x64")
    call = [beamng_path, "-nosteam", "-tcom-listen-ip", "127.0.0.1", "-lua", "extensions.load('tech/techCore');tech_techCore.openServer(25252)", "-userpath", "C:\\Users\\AlessioPrini\\AppData\\Local\\BeamNG.drive"]
    
    process = subprocess.Popen(call, stdin=subprocess.PIPE)

    time.sleep(5)  # Wait for BeamNG to start

    beamng = BeamNGpy("localhost", 25252, home="C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive")
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

    # beamng.scenario.stop()
    beamng.close()

    process.terminate()
    process.wait()

if __name__ == "__main__":
    main()
