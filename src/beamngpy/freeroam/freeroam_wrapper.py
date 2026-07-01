"""
Wrapper for BeamNG's freeroam Lua functionality.

This module provides Python bindings for BeamNG's freeroam_freeroam Lua extension
through queue_lua_command, enabling level loading without creating a Scenario object.

Freeroam API (from BeamNG Lua):
- freeroam_freeroam.startFreeroam(levelPath) - Load a level in freeroam mode
- getMissionFilename() - Get the currently loaded level path (empty if none)
"""

import time
import logging
from typing import Optional

from beamngpy.logging import LOGGER_ID

logger = logging.getLogger(f"{LOGGER_ID}.FreeroamWrapper")


class FreeroamWrapper:
    """
    Wrapper for BeamNG's freeroam Lua functionality.

    Provides Python methods that execute freeroam Lua commands
    via queue_lua_command, allowing level loading and state queries
    without using Scenario objects.
    """

    def __init__(self, beamng_instance):
        """
        Initialize the FreeroamWrapper.

        Args:
            beamng_instance: BeamNG instance to use for Lua command execution
        """
        self.beamng = beamng_instance

    def start_freeroam(self, level_name: str) -> None:
        """
        Send the Lua command to start loading a level in freeroam mode.

        This is asynchronous: the command returns immediately,
        the level loads in background. Use wait_for_level_load() to wait.

        Args:
            level_name: Level folder name (e.g. 'italy', 'west_coast_usa', 'smallgrid')

        Raises:
            RuntimeError: If the command fails
        """
        try:
            lua_code = f"freeroam_freeroam.startFreeroam('/levels/{level_name}/main.level.json')"
            self.beamng.control.queue_lua_command(lua_code, response=False)
            logger.info(f"Freeroam load command sent for level: {level_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to start freeroam for level '{level_name}': {e}")

    def get_mission_filename(self) -> str:
        """
        Get the path of the currently loaded level.

        Returns:
            Level path string (e.g. '/levels/italy/main.level.json')
            or empty string if no level is loaded.
        """
        try:
            lua_code = "return getMissionFilename and getMissionFilename() or ''"
            result = self.beamng.control.queue_lua_command(lua_code, response=True)
            return str(result) if result else ""
        except Exception as e:
            logger.warning(f"Failed to get mission filename: {e}")
            return ""

    def is_level_loaded(self, level_name: str) -> bool:
        """
        Check if a specific level is currently loaded.

        Args:
            level_name: Level folder name to check for

        Returns:
            True if the level is loaded, False otherwise
        """
        mission = self.get_mission_filename()
        return level_name in mission if mission else False

    def wait_for_level_load(
        self, level_name: str, timeout: float = 120, interval: float = 0.2
    ) -> None:
        """
        Poll until the specified level is loaded, or timeout.

        Args:
            level_name: Level folder name to wait for
            timeout: Maximum wait time in seconds (default 120)
            interval: Polling interval in seconds (default 2)

        Raises:
            TimeoutError: If the level doesn't load within timeout
        """
        waited = 0.0
        while waited < timeout:
            if self.is_level_loaded(level_name):
                logger.info(f"Level '{level_name}' loaded after {waited:.0f}s")
                return
            time.sleep(interval)
            waited += interval
            logger.debug(f"Waiting for level '{level_name}' to load... ({waited:.0f}s/{timeout:.0f}s)")

        raise TimeoutError(
            f"Level '{level_name}' did not load within {timeout}s"
        )

    def get_gamestate(self) -> str:
        """
        Get the current game state.

        Returns:
            'menu' if in main menu, 'scenario' if a level/scenario is loaded
        """
        try:
            gs = self.beamng.control.get_gamestate()
            return gs.get("state", "unknown")
        except Exception as e:
            logger.warning(f"Failed to get gamestate: {e}")
            return "unknown"

    def safe_return_to_menu(self) -> None:
        """
        Return to main menu only if not already there.

        IMPORTANT: Calling return_to_main_menu() when already in the menu
        will block BeamNGpy indefinitely. This method checks gamestate first.
        """
        try:
            state = self.get_gamestate()
            if state == "menu":
                logger.debug("Already in menu, skipping return_to_main_menu()")
                return
            self.beamng.control.return_to_main_menu()
            logger.info("Returned to main menu")
        except Exception as e:
            logger.warning(f"Error during safe_return_to_menu: {e}")
