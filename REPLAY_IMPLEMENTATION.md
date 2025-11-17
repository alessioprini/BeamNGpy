# Replay Feature - Implementation Details

## Project Structure

```
src/BeamNGpy/
├── src/beamngpy/
│   ├── api/beamng/
│   │   ├── __init__.py          (updated - added ReplayApi import)
│   │   └── replay.py            (NEW - ReplayApi class)
│   │
│   ├── replay/
│   │   ├── __init__.py          (NEW - module init)
│   │   └── core_replay_wrapper.py (NEW - CoreReplayWrapper class)
│   │
│   └── beamng/
│       └── beamng.py            (updated - added ReplayApi initialization)
│
├── examples/
│   └── replay_example.py        (NEW - usage example)
│
└── docs/
    ├── REPLAY_FEATURE.md        (NEW - user guide)
    └── REPLAY_IMPLEMENTATION.md (NEW - this file)
```

## File Details

### 1. `src/beamngpy/replay/core_replay_wrapper.py`

**Purpose**: Direct wrapper around BeamNG's core_replay Lua extension

**Key Classes**:
- `CoreReplayWrapper` - Main wrapper class

**Methods**:
- `__init__(beamng_instance)` - Initialize wrapper
- `toggle_recording(autoplay_after_stopping)` - Toggle recording on/off
- `start_recording(filename)` - Start recording
- `stop_recording()` - Stop recording
- `cancel_recording()` - Cancel recording without saving
- `load_replay(filepath)` - Load replay file
- `toggle_play()` - Toggle play/pause
- `play(speed)` - Start playback at speed
- `pause(paused)` - Pause/unpause playback
- `stop()` - Stop playback
- `seek(normalized_time)` - Seek to position (0-1)
- `seek_seconds(seconds)` - Seek to seconds (helper)
- `jump(offset)` - Jump by offset seconds
- `set_speed(speed)` - Set playback speed
- `toggle_speed(preset)` - Toggle speed preset
- `get_state()` - Get current state
- `get_position_seconds()` - Get current position
- `get_total_seconds()` - Get total duration
- `is_paused()` - Check if paused
- `get_loaded_file()` - Get loaded file path
- `get_recordings()` - Get list of recordings (with Lua->JSON conversion)
- `get_replay_info()` - Get comprehensive replay metadata

**Key Implementation Detail**:
```python
# All methods use queue_lua_command to execute Lua code:
lua_code = f'core_replay.toggleRecording("{filename}")'
response = self.beamng.control.queue_lua_command(lua_code, response=False)
```

### 2. `src/beamngpy/api/beamng/replay.py`

**Purpose**: High-level Pythonic API wrapper around CoreReplayWrapper

**Key Classes**:
- `ReplayApi` - Main API class

**Methods**:
- `start_recording(filename)` - Start recording
- `stop_recording()` - Stop recording and return filename
- `cancel_recording()` - Cancel recording without saving
- `toggle_recording(filename)` - Toggle recording on/off
- `load_replay(filepath)` - Load replay (validates against available recordings)
- `play(speed)` - Play loaded replay at speed
- `pause()` - Pause playback
- `resume()` - Resume playback
- `stop()` - Stop playback
- `seek(seconds)` - Seek to seconds (converts to normalized 0-1)
- `set_speed(speed)` - Set playback speed
- `get_info()` - Get comprehensive replay info
- `list_replays()` - List available replays

**Design Pattern**:
- Follows BeamNGpy's API pattern (similar to CameraApi, ControlApi, etc.)
- Delegates to CoreReplayWrapper for Lua communication
- Provides cleaner interface for end users

### 3. `src/beamngpy/beamng/beamng.py`

**Changes**:
1. Added import: `from beamngpy.api.beamng import (..., ReplayApi, ...)`
2. Added documentation for `replay` attribute
3. Added in `_setup_api()`: `self.replay = ReplayApi(self)`

**Result**:
- Users can now access replay functionality via `beamng.replay`

### 4. `src/beamngpy/api/beamng/__init__.py`

**Changes**:
- Added: `from .replay import ReplayApi`

**Result**:
- ReplayApi is properly exported from the api.beamng module

## Communication Flow

### Recording Example

```
Python Code:
    beamng.replay.start_recording("test")
            |
            v
    ReplayApi.start_recording()
            |
            v
    CoreReplayWrapper.start_recording()
            |
            v
    Lua Code: if not core_replay.isRecording() then
                  core_replay.toggleRecording("test")
              end
            |
            v
    queue_lua_command() sends to BeamNG
            |
            v
    BeamNG Lua Engine executes core_replay.toggleRecording()
            |
            v
    Recording starts in simulation
```

### Playback Example

```
Python Code:
    beamng.replay.load_replay("test.rpl")
    beamng.replay.play(speed=1.5)
            |
            v
    ReplayApi methods
            |
            v
    CoreReplayWrapper methods
            |
            v
    Lua Code: core_replay.loadReplay("test")
              core_replay.setPlaybackSpeed(1.5)
              core_replay.playReplay()
            |
            v
    queue_lua_command() sends to BeamNG
            |
            v
    BeamNG Lua Engine executes core_replay functions
            |
            v
    Simulation replays recorded state
```

## Error Handling Strategy

All methods in CoreReplayWrapper include try-except blocks:

```python
try:
    lua_code = 'core_replay.toggleRecording()'
    self.beamng.control.queue_lua_command(lua_code, response=False)
except Exception as e:
    raise RuntimeError(f"Failed to toggle recording: {str(e)}")
```

This ensures:
1. BeamNG exceptions are caught
2. User gets descriptive error messages
3. Invalid operations raise RuntimeError with context

## Response Handling

**Non-response Lua Code**:
```python
lua_code = 'core_replay.toggleRecording(false)'
self.beamng.control.queue_lua_command(lua_code, response=False)
```

**Response Lua Code**:
```python
lua_code = 'return core_replay.isPaused()'
response = self.beamng.control.queue_lua_command(lua_code, response=True)
return response.lower() == "true" if isinstance(response, str) else bool(response)
```

**Lua Table to JSON Conversion**:
Special handling for `get_recordings()` - `core_replay.getRecordings()` returns a Lua table which queue_lua_command cannot directly convert. Solution: serialize to JSON in Lua first, then parse in Python.

```python
lua_code = '''
local recordings = core_replay.getRecordings()
local json_array = "["
local first = true
if recordings then
    for key, recording in pairs(recordings) do
        -- Extract name field from recording table
        if not first then json_array = json_array .. "," end
        json_array = json_array .. '"' .. tostring(recording.name or key) .. '"'
        first = false
    end
end
json_array = json_array .. "]"
return json_array
'''
# Then parse JSON in Python
return json.loads(response)
```

The wrapper handles BeamNG's response format (string, bool, dict, or JSON string).

## Integration Points

### 1. Connection Layer
- Uses `beamng.control.queue_lua_command()` for all Lua execution
- Respects BeamNG's msgpack protocol
- Handles socket communication automatically

### 2. API Layer
- Follows BeamNGpy's API design pattern
- Similar structure to other API modules (CameraApi, DebugApi, etc.)
- Integrates into BeamNG object initialization

### 3. Type System
- Uses BeamNGpy's type hints (Optional, Dict, List, etc.)
- Maintains consistency with codebase style

## Testing Considerations

### Unit Testing

```python
def test_start_recording(mock_beamng):
    wrapper = CoreReplayWrapper(mock_beamng)
    wrapper.start_recording("test")
    # Verify queue_lua_command was called with correct Lua code
```

### Integration Testing

```python
def test_full_recording_playback(beamng):
    beamng.replay.start_recording("test")
    # ... run scenario ...
    beamng.replay.stop_recording()

    beamng.replay.load_replay("test.rpl")
    beamng.replay.play()
    # ... verify playback ...
```

### Example Script

See `examples/replay_example.py` for runnable tests.

## Important Implementation Notes

### Seek Normalization
`core_replay.seek()` expects normalized time (0-1), NOT seconds.
- `seek(0.0)` = start
- `seek(0.5)` = middle
- `seek(1.0)` = end

**Wrapper provides helper**: `seek_seconds(seconds)` which auto-converts:
```python
def seek_seconds(self, seconds: float) -> None:
    total_seconds = self.get_total_seconds()
    normalized_time = seconds / total_seconds  # Convert to 0-1
    self.seek(normalized_time)
```

**ReplayApi hides this complexity**: `beamng.replay.seek(5.0)` automatically converts to normalized time.

### Recording Filename Handling
`toggleRecording()` handles filename internally. The `start_recording(filename)` is just for reference tracking in Python - the actual BeamNG replay filename is determined by BeamNG's internal system.

## Performance Characteristics

### Recording
- **CPU Impact**: Minimal (handled by BeamNG)
- **Memory**: Moderate (depends on scenario complexity)
- **Lua Overhead**: Negligible (one command per toggle)

### Playback
- **CPU Impact**: Depends on scenario complexity
- **Memory**: Moderate (replay file loaded in memory)
- **Control Overhead**: Minimal (one command per control action)

## Debugging Tips

### Enable BeamNG Debug Mode
```python
beamng = BeamNGpy("localhost", 64256, debug=True)
# Creates techCapture.*.log files with all protocol messages
```

### Check Replay Info
```python
info = beamng.replay.get_info()
print(f"Status: {info}")
# Shows isPlaying, isPaused, isLoaded, duration, currentTime
```

### List Available Replays
```python
replays = beamng.replay.list_replays()
print(f"Available replays: {replays}")
```

## Future Enhancement Points

1. **Metadata Storage**: Store recording metadata in separate JSON files
2. **Compression**: Implement replay file compression
3. **Filtering**: Record only specific vehicles or sensors
4. **Analytics**: Extract statistics from recorded replays
5. **Batch Processing**: Replay multiple recordings programmatically

## Maintenance Notes

- All code follows PEP 8 style guidelines
- Type hints are used throughout
- Docstrings follow NumPy style
- Error messages are descriptive and actionable
- No external dependencies added (uses existing queue_lua_command)
