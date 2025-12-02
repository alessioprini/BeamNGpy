"""
Wrapper for BeamNG's native core_replay Lua functionality.

This module provides Python bindings for BeamNG's core_replay Lua extension,
enabling recording and playback of complete simulation states including all
vehicles, traffic, and environment through queue_lua_command.

Core_replay API (from BeamNG):
- toggleRecording(autoplayAfterStopping) - Start/stop recording
- loadFile(filename) - Load replay file
- togglePlay() - Play/pause toggle
- pause(v) - Pause (v=true/false)
- stop() - Stop playback
- seek(time) - Seek (time is 0-1 normalized, not seconds)
- jump(offset) - Jump by offset
- setSpeed(speed) - Set playback speed
- toggleSpeed(val) - Toggle speed presets ("realtime", "slowmotion", etc)
- getState() - Get current state
- getPositionSeconds() - Get current position in seconds
- getTotalSeconds() - Get total duration in seconds
- isPaused() - Check if paused
- getLoadedFile() - Get loaded file path
- getRecordings() - Get list of recordings
- cancelRecording() - Cancel recording
"""

from typing import Optional, List, Dict, Any


class CoreReplayWrapper:
    """
    Wrapper for BeamNG's core_replay Lua functionality.

    Provides easy-to-use Python methods that execute core_replay Lua commands
    via queue_lua_command, allowing full control over simulation recording
    and playback.
    """

    def __init__(self, beamng_instance):
        """
        Initialize the CoreReplayWrapper.

        Args:
            beamng_instance: BeamNG instance to use for Lua command execution
        """
        self.beamng = beamng_instance
        self.current_replay_file: Optional[str] = None

    def toggle_recording(self, autoplay_after_stopping: bool = False) -> None:
        """
        Toggle recording on/off using core_replay.toggleRecording().

        Args:
            autoplay_after_stopping: If True, automatically play recording after stopping

        Raises:
            RuntimeError: If toggle fails
        """
        try:
            autoplay_str = "true" if autoplay_after_stopping else "false"
            lua_code = f'core_replay.toggleRecording({autoplay_str})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to toggle recording: {str(e)}")

    def start_recording(self) -> None:
        """
        Start recording.

        Args:
            filename: Optional filename for the replay (just for reference, toggleRecording handles it)

        Raises:
            RuntimeError: If recording start fails
        """
        try:
            lua_code = 'core_replay.toggleRecording(false)'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to start recording: {str(e)}")

    def stop_recording(self) -> None:
        """
        Stop recording.

        Raises:
            RuntimeError: If recording stop fails
        """
        try:
            lua_code = 'core_replay.toggleRecording(false)'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to stop recording: {str(e)}")

    def cancel_recording(self) -> None:
        """
        Cancel current recording (discard it).

        Raises:
            RuntimeError: If cancellation fails
        """
        try:
            lua_code = 'core_replay.cancelRecording()'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to cancel recording: {str(e)}")

    def load_replay(self, filepath: str) -> None:
        """
        Load a replay file for playback.

        Args:
            filepath: Path to the .rpl file to load

        Raises:
            RuntimeError: If replay loading fails
        """
        try:

            lua_code = f'core_replay.loadFile("{filepath}")'
            self.beamng.control.queue_lua_command(lua_code, response=False)
            self.current_replay_file = filepath

        except Exception as e:
            raise RuntimeError(f"Failed to load replay: {str(e)}")

    def toggle_play(self) -> None:
        """
        Toggle play/pause state.

        Raises:
            RuntimeError: If toggle fails
        """
        try:
            lua_code = 'core_replay.togglePlay()'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to toggle play: {str(e)}")

    def play(self, speed: float = 1.0) -> None:
        """
        Play the loaded replay at specified speed.

        Args:
            speed: Playback speed multiplier (1.0 = normal, 2.0 = 2x speed)

        Raises:
            RuntimeError: If playback fails
        """
        try:
            # Set speed first
            lua_code = f'core_replay.setSpeed({speed})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

            # Then toggle play if not already playing
            lua_code = '''
if core_replay.getState() ~= "playing" then
    core_replay.togglePlay()
end
'''
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to play replay: {str(e)}")

    def pause(self, paused: bool = True) -> None:
        """
        Pause/unpause playback.

        Args:
            paused: True to pause, False to resume

        Raises:
            RuntimeError: If pause operation fails
        """
        try:
            paused_str = "true" if paused else "false"
            lua_code = f'core_replay.pause({paused_str})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to pause replay: {str(e)}")

    def stop(self) -> None:
        """
        Stop replay playback.

        Raises:
            RuntimeError: If stop operation fails
        """
        try:
            lua_code = 'core_replay.stop()'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to stop replay: {str(e)}")

    def seek(self, normalized_time: float) -> None:
        """
        Seek to specific position in replay.

        Args:
            normalized_time: Position as 0-1 (0 = start, 1 = end)

        Raises:
            RuntimeError: If seek operation fails
            ValueError: If normalized_time is not in range 0-1
        """
        if not (0.0 <= normalized_time <= 1.0):
            raise ValueError("normalized_time must be between 0.0 and 1.0")

        try:
            lua_code = f'core_replay.seek({normalized_time})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to seek replay: {str(e)}")

    def seek_seconds(self, seconds: float) -> None:
        """
        Seek to specific timestamp in seconds.

        Args:
            seconds: Seconds to seek to

        Raises:
            RuntimeError: If seek operation fails
        """
        try:
            # Get total duration and convert to normalized time
            total_seconds = self.get_total_seconds()
            if total_seconds <= 0:
                raise RuntimeError("Cannot seek: unknown total duration")


            print(f"Seeking to {seconds} seconds out of {total_seconds} total seconds")
            normalized_time = min(1.0, max(0.0, seconds / total_seconds))
            normalized_time += 0.001  # small offset to avoid edge cases 
            self.seek(normalized_time)
            print(f"Seeked to normalized time {normalized_time}")

        except Exception as e:
            raise RuntimeError(f"Failed to seek to {seconds} seconds: {str(e)}")

    def jump(self, offset: float) -> None:
        """
        Jump by offset from current position.

        Args:
            offset: Offset in seconds (can be negative)

        Raises:
            RuntimeError: If jump operation fails
        """
        try:
            lua_code = f'core_replay.jump({offset})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to jump: {str(e)}")

    def set_speed(self, speed: float) -> None:
        """
        Set replay playback speed.

        Args:
            speed: Speed multiplier (1.0 = normal, 2.0 = 2x speed, 0.5 = half speed)

        Raises:
            RuntimeError: If speed setting fails
            ValueError: If speed is not positive
        """
        if speed <= 0:
            raise ValueError("Playback speed must be positive")

        try:
            lua_code = f'core_replay.setSpeed({speed})'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to set playback speed: {str(e)}")

    def toggle_speed(self, speed_preset: str) -> None:
        """
        Toggle to speed preset.

        Args:
            speed_preset: Speed preset ("realtime", "slowmotion", "-1", "^", "v", etc)

        Raises:
            RuntimeError: If toggle fails
        """
        try:
            lua_code = f'core_replay.toggleSpeed("{speed_preset}")'
            self.beamng.control.queue_lua_command(lua_code, response=False)

        except Exception as e:
            raise RuntimeError(f"Failed to toggle speed preset: {str(e)}")

    def get_state(self) -> Optional[str]:
        """
        Get current replay state.

        Returns:
            State string (e.g., "playing", "paused", "idle", etc.)
        """
        try:
            lua_code = 'return core_replay.getState()'
            response = self.beamng.control.queue_lua_command(lua_code, response=True)
            return str(response) if response else None

        except Exception as e:
            print(f"Warning: Failed to get replay state: {str(e)}")
            return None

    def get_position_seconds(self) -> float:
        """
        Get current playback position in seconds.

        Returns:
            Current position in seconds
        """
        try:
            lua_code = 'return core_replay.getPositionSeconds()'
            response = self.beamng.control.queue_lua_command(lua_code, response=True)
            return float(response) if response else 0.0

        except Exception as e:
            print(f"Warning: Failed to get position: {str(e)}")
            return 0.0

    def get_total_seconds(self) -> float:
        """
        Get total replay duration in seconds.

        Returns:
            Total duration in seconds
        """
        try:
            lua_code = 'return core_replay.getTotalSeconds()'
            response = self.beamng.control.queue_lua_command(lua_code, response=True)
            return float(response) if response else 0.0

        except Exception as e:
            print(f"Warning: Failed to get total duration: {str(e)}")
            return 0.0

    def is_paused(self) -> bool:
        """
        Check if replay is paused.

        Returns:
            True if paused, False otherwise
        """
        try:
            lua_code = 'return core_replay.isPaused()'
            response = self.beamng.control.queue_lua_command(lua_code, response=True)

            if isinstance(response, bool):
                return response
            if isinstance(response, str):
                return response.lower() == "true"
            return bool(response)

        except Exception as e:
            print(f"Warning: Failed to check pause state: {str(e)}")
            return False

    def get_loaded_file(self) -> Optional[str]:
        """
        Get path of currently loaded replay file.

        Returns:
            Path to loaded file or None if no file loaded
        """
        try:
            lua_code = 'return core_replay.getLoadedFile()'
            response = self.beamng.control.queue_lua_command(lua_code, response=True)
            return str(response) if response else None

        except Exception as e:
            print(f"Warning: Failed to get loaded file: {str(e)}")
            return None

    def get_recordings(self) -> List[str]:
        """
        Get list of available recording files.

        Returns:
            List of recording filenames
        """
        try:
            # Convert Lua table to JSON string
            # core_replay.getRecordings() returns table of tables, extract name or path field
            lua_code = '''
local recordings = core_replay.getRecordings()
local json_array = "["
local first = true
if recordings then
    for key, recording in pairs(recordings) do
        local name = ""
        -- Try to get name from different possible fields
        if type(recording) == "string" then
            name = recording
        elseif type(recording) == "table" then
            -- Try common field names
            if recording.name then name = recording.name
            elseif recording.path then name = recording.path
            elseif recording.filename then name = recording.filename
            else name = tostring(key)
            end
        else
            name = tostring(recording)
        end

        if not first then json_array = json_array .. "," end
        json_array = json_array .. '"' .. tostring(name) .. '"'
        first = false
    end
end
json_array = json_array .. "]"
return json_array
'''
            response = self.beamng.control.queue_lua_command(lua_code, response=True)

            if response:
                import json
                # If it's a string, try to parse as JSON
                if isinstance(response, str):
                    try:
                        return json.loads(response)
                    except (json.JSONDecodeError, ValueError):
                        pass

            return []

        except Exception as e:
            print(f"Warning: Failed to list recordings: {str(e)}")
            return []

    def get_replay_info(self) -> Dict[str, Any]:
        """
        Get comprehensive replay information.

        Returns:
            Dictionary with state, position, duration, etc.
        """
        try:
            info = {
                "state": self.get_state(),
                "position_seconds": self.get_position_seconds(),
                "total_seconds": self.get_total_seconds(),
                "is_paused": self.is_paused(),
                "loaded_file": self.get_loaded_file(),
            }
            return info

        except Exception as e:
            print(f"Warning: Failed to get replay info: {str(e)}")
            return {}
