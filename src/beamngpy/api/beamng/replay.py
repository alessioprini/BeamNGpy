"""
Replay API for BeamNGpy - wrapper around core_replay Lua extension.
"""

from beamngpy.replay import CoreReplayWrapper


class ReplayApi:
    """
    API for replay functionality using BeamNG's native core_replay extension.

    This API provides convenient methods to record and playback complete simulation
    state (vehicles, traffic, environment) using BeamNG's core_replay Lua extension
    via queue_lua_command.

    Args:
        beamng: An instance of the simulator.
    """

    def __init__(self, beamng):
        """
        Initialize ReplayApi.

        Args:
            beamng: BeamNG instance
        """
        self.beamng = beamng
        self._core_replay = CoreReplayWrapper(beamng)

    def start_recording(self) -> None:
        """
        Start recording simulation state to a replay file.

        Args:
            filename: Name of the replay file (without .rpl extension)

        Example:
            ```python
            beamng.replay.start_recording("my_scenario_run")
            # ... run simulation ...
            beamng.replay.stop_recording()
            ```
        """
        self._core_replay.start_recording()

    def stop_recording(self) -> str:
        """
        Stop recording and return the replay filename.

        Returns:
            Filename of the recorded replay

        Example:
            ```python
            filename = beamng.replay.stop_recording()
            print(f"Replay saved to: {filename}")
            ```
        """
        return self._core_replay.stop_recording()

    def cancel_recording(self) -> None:
        """
        Cancel the current recording without saving.

        Example:
            ```python
            beamng.replay.cancel_recording()
            ```
        """
        self._core_replay.cancel_recording()

    def toggle_recording(self, filename: str = None) -> bool:
        """
        Toggle recording on/off.

        Args:
            filename: Optional filename for the replay

        Returns:
            True if recording is now active, False if stopped
        """
        return self._core_replay.toggle_recording(filename)

    def load_replay(self, filepath: str) -> None:
        """
        Load a replay file for playback.

        Args:
            filepath: Path to the .rpl replay file

        Example:
            ```python
            beamng.replay.load_replay("replays/my_scenario_run.rpl")
            beamng.replay.play()
            ```
        """

        ll = self._core_replay.get_recordings()
        if filepath not in ll:
            raise RuntimeError(f"Replay file '{filepath}' not found among available recordings: {ll}")

        self._core_replay.load_replay(filepath)

    def play(self, speed: float = 1.0) -> None:
        """
        Play the loaded replay at specified speed.

        Args:
            speed: Playback speed multiplier (1.0 = normal, 2.0 = 2x)

        Example:
            ```python
            beamng.replay.play(speed=1.5)  # Play at 1.5x speed
            ```
        """
        self._core_replay.play(speed)

    def pause(self) -> None:
        """Pause replay playback."""
        self._core_replay.pause(True)

    def resume(self) -> None:
        """Resume paused replay playback."""
        self._core_replay.pause(False)

    def stop(self) -> None:
        """Stop replay playback."""
        self._core_replay.stop()

    def seek(self, seconds: float) -> None:
        """
        Seek to specific timestamp in replay.

        Args:
            seconds: Timestamp in seconds

        Example:
            ```python
            beamng.replay.seek(5.0)  # Jump to 5 second mark
            ```
        """
        self._core_replay.seek_seconds(seconds)

    def set_speed(self, speed: float) -> None:
        """
        Set replay playback speed.

        Args:
            speed: Speed multiplier (1.0 = normal)
        """
        self._core_replay.set_speed(speed)

    def get_info(self) -> dict:
        """
        Get current replay information.

        Returns:
            Dictionary with replay status and metadata

        Example:
            ```python
            info = beamng.replay.get_info()
            print(f"Replay duration: {info.get('duration')}")
            print(f"Current time: {info.get('currentTime')}")
            ```
        """
        res = self._core_replay.get_replay_info()
        return res

    def list_replays(self) -> list:
        """
        List available replay files.

        Args:
            folder: Optional folder to search in

        Returns:
            List of replay filenames
        """
        return self._core_replay.get_recordings()
