"""
Example script demonstrating replay recording and playback functionality.

This script shows how to:
1. Record a simulation replay using core_replay
2. Play back the recorded replay
3. Control playback (pause, resume, seek, speed)
"""

from beamngpy import BeamNGpy, Scenario, Vehicle
import time


def record_replay_example():
    """
    Example of recording a replay during a scenario run.
    """
    print("=" * 60)
    print("REPLAY RECORDING EXAMPLE")
    print("=" * 60)

    # Create BeamNGpy instance
    beamng = BeamNGpy("localhost", 64256, home="C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive", debug=False)

    try:
        # Open the simulator
        print("\n1. Opening BeamNG simulator...")
        beamng.open()

        a = beamng.control.get_gamestate()
        print(a)


        # Create a simple scenario
        print("2. Creating scenario...")
        # scenario = Scenario("tech_ground", "replay_test_scenario")
        scenario = Scenario("Gridmap_V2", "custom_scenario")

        # Add a vehicle
        # vehicle = Vehicle("ego_vehicle", model="etk800")
        vehicle = Vehicle("ego", model="etk800", color="White")

        scenario.add_vehicle(vehicle, pos=(0, 0, 100))

        scenario.make(beamng)

        # Load and start the scenario
        print("3. Loading scenario...")
        beamng.scenario.load(scenario)
        beamng.scenario.start()

        # Wait for scenario to start
        time.sleep(2)


        a = beamng.control.get_gamestate()
        print(a)


        # Start recording
        print("4. Starting replay recording...")
        replay_filename = "example_replay"
        beamng.replay.start_recording()

        # Run the scenario for 10 seconds while recording
        print("5. Running simulation (10 seconds)...")
        for i in range(10):  # 10 seconds at 60 FPS
            # Simulate some vehicle input
            if i < 2.0:
                vehicle.control(throttle=1.0)  # Accelerate
            elif i < 3.0:
                vehicle.control(steering=0.5)  # Turn right
            elif i < 4.0:
                vehicle.control(steering=-0.5)  # Turn left
            else:
                vehicle.control(throttle=0.0, brake=0.5)  # Brake

            # Step the simulation
            time.sleep(1.0)


            if i % 100 == 0:
                print(f"   ... {i // 100}s recorded")

        # Stop recording
        print("6. Stopping replay recording...")
        saved_file = beamng.replay.stop_recording()
        print(f"   Replay saved to: {saved_file}.rpl")

        # Stop the scenario
        print("7. Stopping scenario...")
        beamng.scenario.stop()

        return saved_file

    finally:
        # Close the simulator
        print("\n8. Closing simulator...")
        beamng.close()


def playback_replay_example(replay_file):
    """
    Example of playing back a recorded replay.
    """
    print("\n" + "=" * 60)
    print("REPLAY PLAYBACK EXAMPLE")
    print("=" * 60)

    # Create BeamNGpy instance
    # beamng = BeamNGpy("localhost", 64256, debug=False)
    beamng = BeamNGpy("localhost", 64256, home="C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive", debug=False)

    try:
        # Open the simulator
        print("\n1. Opening BeamNG simulator...")
        beamng.open()

        # # Create and load the same scenario
        # print("2. Creating scenario...")
        # # scenario = Scenario("tech_ground", "replay_test_scenario")
        # scenario = Scenario("italy", "camera_streaming")

        # # vehicle = Vehicle("ego_vehicle", model="etk800")
        # vehicle = Vehicle("ego", model="etk800", color="White")

        # scenario.add_vehicle(vehicle, pos=(0, 0, 100))
        # scenario.make(beamng)

        # print("3. Loading scenario...")
        # beamng.scenario.load(scenario)
        # beamng.scenario.start()

        # Wait for scenario to start
        time.sleep(2)


        print("4. Listing available replays...")
        replays = beamng.replay.list_replays()

        if replays:
            print(f"   Found {len(replays)} replay(s):")
            for replay in replays:
                print(f"   - {replay}")
        else:
            print("   No replays found")


        # Load the replay
        print(f"5. Loading replay: {replay_file}.rpl")
        replay_path = f"replays/{replay_file}.rpl"
        beamng.replay.load_replay(replay_path)

        # Get replay info
        print("5. Getting replay information...")

        init = time.time()
        a = beamng.control.get_gamestate()
        while a['state'] == 'menu':
            a = beamng.control.get_gamestate()
            time.sleep(1)

        # Play at normal speed
        print("6. Playing replay at 1.0x speed...")
        
        print("get info block the execution for some reason")
        print(beamng.replay.get_info()["state"])
        print("unlocked")


        beamng.replay.play(speed=1.0)
        beamng.replay.pause()
        beamng.replay.seek(0.0)
        time.sleep(0.5)
        beamng.replay.resume()

        # Wait for playback to reach halfway
        print("   Waiting 5 seconds...")
        init = time.time()
        while time.time() - init < 10.0:
            print("   Replay status:")
            ii = beamng.replay.get_info()
            print(ii["state"])
            print(ii["position_seconds"])
            print(ii["total_seconds"])
            print(ii["is_paused"])
            print(ii["loaded_file"])
            print("-----")
            time.sleep(1)


        # # Pause the replay
        # print("7. Pausing replay...")
        # beamng.replay.pause()
        # time.sleep(2)

        # # Resume the replay
        # print("8. Resuming replay...")
        # beamng.replay.resume()
        # time.sleep(3)

        # # Seek to specific timestamp
        # print("9. Seeking to 5 second mark...")
        # beamng.replay.seek(5.0)
        # time.sleep(2)

        # # Play at 2x speed
        # print("10. Playing at 2.0x speed...")
        # beamng.replay.set_speed(2.0)
        # time.sleep(10)

        # # Stop the replay
        # print("11. Stopping replay...")
        beamng.replay.stop()

        # # Stop the scenario
        # print("12. Stopping scenario...")
        # # beamng.scenario.stop()

    finally:
        # Close the simulator
        print("\n13. Closing simulator...")
        beamng.close()


def list_replays_example():
    """
    Example of listing available replays.
    """
    print("\n" + "=" * 60)
    print("LIST REPLAYS EXAMPLE")
    print("=" * 60)

    # Create BeamNGpy instance
    # beamng = BeamNGpy("localhost", 64256, debug=False)
    beamng = BeamNGpy("localhost", 64256, home="C:\\Users\\AlessioPrini\\Documents\\AMBUSIM\\AmbuSim.BeamNG.drive", debug=False)

    try:
        # Open the simulator
        print("\n1. Opening BeamNG simulator...")
        beamng.open()

        # List available replays
        print("2. Listing available replays...")
        replays = beamng.replay.list_replays()

        if replays:
            print(f"   Found {len(replays)} replay(s):")
            for replay in replays:
                print(f"   - {replay}")
        else:
            print("   No replays found")

    finally:
        # Close the simulator
        print("\n3. Closing simulator...")
        beamng.close()


def full_replay_workflow():
    """
    Complete workflow: record -> playback -> analyze.
    """
    print("\n" + "=" * 60)
    print("FULL REPLAY WORKFLOW")
    print("=" * 60)

    # Record a replay
    saved_file = record_replay_example()

    # Playback the recorded replay
    playback_replay_example(saved_file)

    # List available replays
    list_replays_example()

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    """
    Run examples.

    Choose which example to run by uncommenting/commenting the function calls below.
    """

    # Run full workflow (record, playback, list)
    # full_replay_workflow()

    # Or run individual examples:

    # Record a replay
    saved_file = record_replay_example()
    # list_replays_example()
    # Playback the recorded replay
    # playback_replay_example("202-11-17_13-33-22 gridmap_v2")
    # playback_replay_example("2025-11-17_13-33-22 gridmap_v2")
    

    # List available replays
    # list_replays_example()
