# BeamNG Freeroam Mode — API Reference


## Overview

Freeroam mode loads a BeamNG.drive level **without creating a `Scenario` object**. It uses the same Lua function that the game calls from the main menu. After loading, the desired vehicle is spawned replacing the default one.

### Difference vs Scenario

| | Scenario | Freeroam |
|---|---|---|
| **Loading** | `beamngpy.Scenario` → `load()` → `start()` | Direct Lua command |
| **Vehicle** | Added to scenario **before** load | Spawned **after** level load |
| **Load Detection** | Synchronous (`load()` blocks) | Asynchronous polling |

---

## 1. Level Loading

```python
bng.queue_lua_command(
    "freeroam_freeroam.startFreeroam('/levels/<LEVEL_NAME>/main.level.json')"
)
```

- `<LEVEL_NAME>` = level folder name (e.g. `italy`, `west_coast_usa`, `smallgrid`)
- The command is **asynchronous**: it returns immediately, the level loads in background

---

## 2. Polling for Load Completion

After sending the load command, poll cyclically:

```lua
-- BeamNG global Lua function:
getMissionFilename()
-- Returns the path of the loaded level (e.g. "/levels/italy/main.level.json")
-- Returns empty string if no level is loaded
```

> The guard `getMissionFilename and getMissionFilename() or ''` is a Lua pattern
> to avoid errors if the function is not yet available: *"if exists, call it;
> otherwise return empty string"*.

### Python Example (beamngpy)

```python
# Lua command to send to check if a level is loaded
lua_cmd = "getMissionFilename and getMissionFilename() or ''"
result = bng.queue_lua_command(lua_cmd)

# result = "/levels/italy/main.level.json"  → level loaded
# result = ""                                → no level loaded
```

---

## 3. Vehicle Spawn (after loading)

Once the level is loaded, the Freeroam default vehicle is already present. To replace it:

```python
from beamngpy import Vehicle

vehicle = Vehicle(
    "vehicle_name",
    model="model",
    part_config="path/config.pc",
)

# Replaces the existing vehicle
bng.vehicles.replace(vehicle, old_vehicle="name_of_vehicle_to_replace")
```

### Important Notes
- `old_vehicle` must be the name of the **currently present vehicle** in the level, not the name of the new one
- In Freeroam the default vehicle is the one defined by the game.
- ⚠️ If `replace` fails (vehicle not found), handle the exception. A fallback `spawn()` will **add an extra vehicle** without removing the existing one — check if this is desired behavior as you would end up with two vehicles side-by-side.

---

## 4. Stop and Return to Menu

I normally use the following command, and it is the same for both scenario and freeroam.

```python
bng.control.return_to_main_menu()
```

---

## 5. Complete Sequence

```
1. Connect via BeamNG        →  bng = BeamNGpy(...).open()
2. Load Freeroam Level       →  queue_lua_command("freeroam_freeroam.startFreeroam(...)")
3. Wait for Load             →  poll getMissionFilename() every 1s (max 60s)
4. Spawn/Replace Vehicle     →  bng.vehicles.replace(new_vehicle, old_vehicle=current)
5. Configure Environment     →  time of day, weather, traffic (optional)
6. ... active session ...
7. Stop                      →  bng.control.return_to_main_menu()
```

---

## 6. Runtime Vehicle Change

Currently not a function in the current UI, but if needed, to change vehicle during an active session (both Scenario and Freeroam):

```python
new_vehicle = Vehicle("new_name", model="model", ...)
bng.vehicles.replace(new_vehicle, old_vehicle="current_active_vehicle_name")
```

**Common Error**: passing the name of the *new* vehicle as `old_vehicle` — this matches nothing and spawns a duplicate. You must always track the name of the currently active vehicle and pass that.
<!--  -->