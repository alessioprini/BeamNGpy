"""
Lua-based replay recorder for capturing complete simulation state.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .formats import JSONReplayFormat, ReplayMetadata, ReplayFrame


class LuaRecorder:
    """
    Records simulation state using Lua commands via queue_lua_command.

    This recorder captures the complete simulation state including all vehicles,
    traffic, environment settings, and physics state by executing Lua queries
    on the BeamNG side.
    """

    def __init__(self, beamng_instance):
        """
        Initialize the LuaRecorder.

        Args:
            beamng_instance: BeamNG instance to record from
        """
        self.beamng = beamng_instance
        self.recording = False
        self.frames: List[ReplayFrame] = []
        self.metadata = ReplayMetadata()
        self.start_time: Optional[float] = None

    def start_recording(
        self,
        scenario_name: str = "",
        description: str = "",
    ) -> None:
        """
        Start recording simulation state.

        Args:
            scenario_name: Name of the scenario being recorded
            description: Optional description of the recording
        """
        if self.recording:
            raise RuntimeError("Recording is already in progress")

        self.recording = True
        self.frames = []
        self.metadata = ReplayMetadata()
        self.metadata.scenario = scenario_name
        self.metadata.description = description
        self.metadata.creation_time = datetime.now().isoformat()

        # Get initial simulation time
        self.start_time = self._get_simulation_time()

    def stop_recording(self) -> None:
        """Stop recording and calculate metadata."""
        if not self.recording:
            raise RuntimeError("Recording is not in progress")

        self.recording = False

        if self.frames:
            self.metadata.frame_count = len(self.frames)
            self.metadata.duration = self.frames[-1].timestamp - self.frames[0].timestamp

    def record_frame(self) -> None:
        """
        Capture current simulation state and add it to recording.

        This method queries the Lua side for the complete simulation state,
        including all vehicles and environment data.
        """
        if not self.recording:
            raise RuntimeError("Recording is not in progress")

        try:
            current_time = self._get_simulation_time()
            if self.start_time is None:
                self.start_time = current_time

            timestamp = current_time - self.start_time

            # Capture complete simulation state via Lua
            lua_state = self._capture_simulation_state()

            # Create and store frame
            frame = ReplayFrame(timestamp=timestamp, lua_state=lua_state)
            self.frames.append(frame)

        except Exception as e:
            raise RuntimeError(f"Failed to record frame: {str(e)}")

    def save_replay(self, filepath: str) -> None:
        """
        Save recorded replay to file.

        Args:
            filepath: Path to save the replay file (.json)
        """
        if self.recording:
            raise RuntimeError("Cannot save while recording is in progress")

        if not self.frames:
            raise ValueError("No frames to save")

        # Prepare data structure
        data = {
            "metadata": self.metadata.to_dict(),
            "frames": [frame.to_dict() for frame in self.frames],
        }

        # Save using JSON format
        JSONReplayFormat.save(data, filepath)

    def _get_simulation_time(self) -> float:
        """
        Get current simulation time via Lua.

        Returns:
            Current simulation time in seconds
        """
        lua_code = "return SimulationManager:getCurrentSimulationTime()"
        response = self.beamng.control.queue_lua_command(lua_code, response=True)

        if response is None:
            # Fallback if time query fails
            return 0.0

        try:
            return float(response)
        except (ValueError, TypeError):
            return 0.0

    def _capture_simulation_state(self) -> Dict[str, Any]:
        """
        Capture complete simulation state via Lua.

        This executes a Lua command that returns the state of all vehicles,
        environment settings, and other relevant simulation data.

        Returns:
            Dictionary containing the simulation state
        """
        # Build comprehensive Lua query
        lua_code = """
local state = {}

-- Get all active vehicles
state.vehicles = {}
for vehicleName, vehicle in pairs(be:getObjectByName("sim:world"):findClassObjects("BeamNGVehicle")) do
    local veh_data = {}
    veh_data.name = vehicleName

    -- Get vehicle position and rotation
    local pos = vehicle:getPosition()
    veh_data.pos = {x = pos.x, y = pos.y, z = pos.z}

    local rot = vehicle:getRotation()
    veh_data.rot = {x = rot.x, y = rot.y, z = rot.z, w = rot.w}

    -- Get vehicle velocity
    local vel = vehicle:getVelocity()
    veh_data.vel = {x = vel.x, y = vel.y, z = vel.z}

    -- Get vehicle damage and parts
    veh_data.damage = vehicle:getTotalDamage()

    state.vehicles[vehicleName] = veh_data
end

-- Get environment data
state.environment = {}
state.environment.time_of_day = core_environment.getTimeOfDay()
state.environment.weather = core_environment.getWeatherType()

-- Get simulation speed
state.simulation_speed = Engine.State.dt

return state
"""

        try:
            response = self.beamng.control.queue_lua_command(lua_code, response=True)
            if response is not None:
                # Parse the Lua response (should be JSON or dict)
                if isinstance(response, str):
                    return json.loads(response)
                return response
            else:
                return {}
        except Exception as e:
            print(f"Warning: Failed to capture full simulation state: {e}")
            return {}

    def get_frame_count(self) -> int:
        """Get number of recorded frames."""
        return len(self.frames)

    def is_recording(self) -> bool:
        """Check if recording is active."""
        return self.recording
