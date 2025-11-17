# BeamNGpy Replay Feature

## Overview

The Replay feature in BeamNGpy provides a complete solution for recording and playing back simulation scenarios using BeamNG's native `core_replay` Lua extension.

This feature allows you to:
- **Record** complete simulation state (all vehicles, traffic, environment) to `.rpl` files
- **Playback** recorded replays with full fidelity
- **Control** playback (pause, resume, seek, speed control)
- **Manage** replay files

## Architecture

The replay feature is built on three main components:

### 1. CoreReplayWrapper (`src/beamngpy/replay/core_replay_wrapper.py`)

Low-level wrapper around BeamNG's `core_replay` Lua extension. It directly executes Lua commands via `queue_lua_command` to control recording and playback.

**Key Methods:**
- `start_recording(filename)` - Start recording
- `stop_recording()` - Stop recording
- `toggle_recording(autoplay_after_stopping)` - Toggle recording state
- `cancel_recording()` - Cancel recording without saving
- `load_replay(filepath)` - Load a replay file
- `play(speed)` - Play loaded replay
- `pause(paused)` / `toggle_play()` - Control playback
- `stop()` - Stop playback
- `seek(normalized_time)` - Seek to normalized position (0-1)
- `seek_seconds(seconds)` - Seek to specific seconds
- `jump(offset)` - Jump by offset
- `set_speed(speed)` - Set playback speed
- `toggle_speed(preset)` - Toggle speed preset
- `get_state()` - Get current replay state
- `get_position_seconds()` - Get current position
- `get_total_seconds()` - Get total duration
- `is_paused()` - Check if paused
- `get_loaded_file()` - Get loaded file path
- `get_recordings()` - Get list of recordings
- `get_replay_info()` - Get comprehensive replay metadata

### 2. ReplayApi (`src/beamngpy/api/beamng/replay.py`)

High-level API integrated into BeamNGpy. Provides a clean, Pythonic interface to the replay functionality.

**Key Methods:**
```python
beamng.replay.start_recording("my_run")
beamng.replay.stop_recording()
beamng.replay.cancel_recording()
beamng.replay.toggle_recording()

beamng.replay.load_replay("replays/my_run.rpl")
beamng.replay.play(speed=1.5)
beamng.replay.pause()
beamng.replay.resume()
beamng.replay.stop()

beamng.replay.seek(5.0)          # Seek to 5 seconds
beamng.replay.set_speed(2.0)      # 2x speed
beamng.replay.toggle_play()       # Toggle play/pause

beamng.replay.get_info()          # Get full status
beamng.replay.list_replays()      # List available replays
```

### 3. Integration with BeamNG

The feature integrates seamlessly with BeamNGpy through the `ReplayApi` class, accessible via:
```python
beamng.replay  # Access to all replay functionality
```

## How It Works

### Recording

When you call `beamng.replay.start_recording()`, the following happens:

1. CoreReplayWrapper sends a Lua command to BeamNG: `core_replay.toggleRecording("filename")`
2. BeamNG's native core_replay extension starts recording all simulation state
3. Every frame, all vehicles, traffic, environment, and physics state is recorded
4. When `beamng.replay.stop_recording()` is called, recording stops and the `.rpl` file is saved

### Playback

When you call `beamng.replay.load_replay()` and `beamng.replay.play()`:

1. Lua command loads the replay: `core_replay.loadFile("filepath")`
2. Lua command sets speed: `core_replay.setSpeed(speed)`
3. Lua command starts playback: `core_replay.togglePlay()` (if not already playing)
4. BeamNG reconstructs the entire scenario state from the recording
5. All vehicles, traffic, and environment are reproduced exactly as recorded
6. Playback can be controlled via:
   - `pause(v)` - Pause/unpause
   - `stop()` - Stop playback
   - `seek(normalized_time)` - Seek (0-1)
   - `setSpeed(speed)` - Change speed

## Protocol Flow

```
BeamNGpy (Python)
    |
    +-- queue_lua_command()
            |
            v
    BeamNG Lua Engine (core_replay extension)
            |
            +-- Simulation State Recording/Playback
            |
            +-- File I/O (.rpl files)
            |
            v
    Returns Response
```

## Usage Examples

### Basic Recording

```python
from beamngpy import BeamNGpy, Scenario, Vehicle

beamng = BeamNGpy("localhost", 64256)
beamng.open()

# Load scenario
scenario = Scenario("tech_ground", "test")
vehicle = Vehicle("car", model="etk800")
scenario.add_vehicle(vehicle)
beamng.load_scenario(scenario)
beamng.start_scenario()

# Record
beamng.replay.start_recording("run_1")
# ... run simulation ...
beamng.replay.stop_recording()

beamng.close()
```

### Playback with Control

```python
beamng.replay.load_replay("replays/run_1.rpl")
beamng.replay.play(speed=1.0)

# Pause at 5 seconds
import time
time.sleep(5)
beamng.replay.pause()

# Resume and speed up
time.sleep(2)
beamng.replay.resume()
beamng.replay.set_speed(2.0)

# Seek to different point
beamng.replay.seek(10.0)
```

### Get Replay Information

```python
info = beamng.replay.get_info()
print(f"Playing: {info['isPlaying']}")
print(f"Duration: {info['duration']}")
print(f"Current Time: {info['currentTime']}")
```

## Lua API Used

The replay feature uses the following core_replay Lua functions:

### Recording
- `core_replay.toggleRecording(autoplayAfterStopping)` - Start/stop recording
- `core_replay.cancelRecording()` - Cancel recording without saving

### Playback
- `core_replay.loadFile(filepath)` - Load replay file
- `core_replay.togglePlay()` - Play/pause toggle
- `core_replay.pause(v)` - Pause (v=true/false)
- `core_replay.stop()` - Stop playback
- `core_replay.seek(normalized_time)` - Seek to position (0-1)
- `core_replay.jump(offset)` - Jump by offset seconds
- `core_replay.setSpeed(speed)` - Set playback speed
- `core_replay.toggleSpeed(preset)` - Toggle speed presets

### Status/Query
- `core_replay.getState()` - Get current state
- `core_replay.isPaused()` - Check if paused
- `core_replay.getPositionSeconds()` - Get current position in seconds
- `core_replay.getTotalSeconds()` - Get total duration in seconds
- `core_replay.getLoadedFile()` - Get loaded file path

### File Management
- `core_replay.getRecordings()` - Get list of available replays

## Error Handling

The wrapper includes error handling for common issues:

```python
try:
    beamng.replay.start_recording("test")
except RuntimeError as e:
    print(f"Failed to start recording: {e}")

try:
    beamng.replay.load_replay("nonexistent.rpl")
except RuntimeError as e:
    print(f"Failed to load replay: {e}")
```

## Performance Considerations

- **Recording**: No additional performance impact beyond BeamNG's native recording
- **Playback**: Controlled by BeamNG, varies based on scenario complexity
- **File Size**: Depends on scenario complexity and duration
- **Speed Control**: 0.5x to 4.0x speeds typically supported

## Example Script

See `examples/replay_example.py` for a complete working example that demonstrates:
- Recording a scenario
- Playing back the recording
- Controlling playback
- Listing replays

## Testing

To test the replay feature:

1. Ensure BeamNG.tech is running
2. Run the example script: `python examples/replay_example.py`
3. Check the replays folder for generated `.rpl` files

## Limitations

- Replays are scenario-specific (must load same scenario to playback)
- Playback speed varies based on system performance
- Some physics-based interactions may vary between recording and playback
- Network traffic between Python and Lua may affect real-time performance

## Future Enhancements

Potential improvements:
- Replay compression
- Selective recording (specific vehicles/sensors)
- Replay analysis tools
- Automatic replay metadata extraction
- Batch replay processing
