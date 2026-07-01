# BeamNG.drive: Scenario Mode vs. Freeroam Mode

This document details the technical and functional differences between loading a level in **Scenario Mode** (via `beamngpy.Scenario`) and **Freeroam Mode** (native load).

---

## 1. Fundamental Difference

### **Scenario Mode (Injection)**
- **Concept:** A "Mission" injected into a level.
- **Mechanism:** `beamngpy` generates a temporary `mission_file.json` and `flow.json` in the user folder, defining vehicles, routes, and logic *before* the level loads.
- **State:** The game enters a "Mission State".
    - Captures the UI (Scenario UI layout).
    - Restricts certain actions (e.g., free camera might be limited, vehicle switching might be disabled by default).
    - Has a definitive "Start" and "Finish" state (Success/Fail).

### **Freeroam Mode (Native)**
- **Concept:** The raw sandbox experience.
- **Mechanism:** The game loads the level directly (like clicking "Freeroam" in the main menu).
- **State:** The game enters "Freeroam State".
    - Uses the player's default or saved UI layout.
    - No restrictions on gameplay (spawn, teleport, change time, modify gravity).
    - No "Win/Loss" condition.

---

## 2. Technical Comparison

| Feature | Scenario Mode (`beamngpy.Scenario`) | Freeroam Mode (Native Load) |
| :--- | :--- | :--- |
| **Loading** | **Slower**: Generates files, injects prefabs, then loads. | **Faster**: Loads the level definition directly. |
| **Vehicle Spawn** | Defined **pre-load**. Vehicles are part of the mission file. | Performed **post-load**. You must wait for the level, then spawn/replace. |
| **Isolation** | **High**. Changes to the world (broken props) reset when the scenario restarts. | **Low**. Damage/debris persists until you manually reset or reload the level. |
| **Stability** | **High consistency**. Every run starts exactly the same way (defined by code). | **Variable**. Depends on previous state if not carefully cleaned up. |
| **Python Control** | Full control via `beamngpy` API wrapper. | Full control via Python, but relies more on raw Lua commands. |

---

## 3. UI Customization & HUD

This is the most significant difference for end-users and developers.

### **Scenario Mode UI**
- **Restricted / Custom Layout**: Scenarios typically force a specific set of UI apps (Race countdown, checkpoints, damage app).
- **Pros**: You can design a custom "Ambusim" UI layout and force it to appear every time the simulation runs. The user cannot easily mess it up.
- **Cons**: The user *cannot* easily move or add apps unless the scenario explicitly allows it.

### **Freeroam Mode UI**
- **User Persisted Layout**: The game loads whatever UI layout the user had last time they played Freeroam.
- **Pros**: Familiarity. If the user likes their speedometer in the top-left, it stays there.
- **Cons**: You cannot guarantee what the user sees. They might have closed all apps, or have the screen cluttered with debug windows.
- **Workaround**: You can force a specific UI layout via Lua commands (`extensions.core_gamestate.setGameState('freeroam', 'layout_name')`) after loading, but it overrides the user's preference.

---

## 4. When to Choose Which?

### **Choose Scenario Mode If:**
- You need a **controlled experiment** (e.g., "Drive from A to B within 60 seconds").
- You need to **detect pass/fail** conditions automatically.
- You want to **enforce a clean UI** specific to your simulator (e.g., hiding game menus, showing only your custom dashboard).
- You rely heavily on **pre-defined paths** (AI ScriptAI paths) that must be loaded with the level.

### **Choose Freeroam Mode If:**
- You want a **"Sandbox"** experience (drive anywhere, do anything).
- You are developing a tool where the **user** decides what to do (e.g., a trainer, a vehicle tester).
- You want the **fastest possible boot time** into the map.
- You need full access to BeamNG's native menu system (vehicle selector, parts config) without mission restrictions.

---

### Summary
**Scenario** is for **Content** (Missions, Tests).
**Freeroam** is for **Context** (Environment, Sandbox).

For **Ambusim**, if the goal is strictly "Test functionality of the ambulance", **Freeroam** is often better because it removes the overhead of mission logic and allows the user to use the game's native tools (like dragging the car, resetting physics) without the mission "failing" or resetting unexpectedly.
