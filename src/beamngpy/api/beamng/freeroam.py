"""
Freeroam API for BeamNGpy - wrapper around freeroam_freeroam Lua extension.
"""

import logging

from beamngpy.freeroam import FreeroamWrapper
from beamngpy.logging import LOGGER_ID

logger = logging.getLogger(f"{LOGGER_ID}.FreeroamApi")


class FreeroamApi:
    """
    API for freeroam functionality using BeamNG's freeroam_freeroam Lua extension.

    This API provides methods to load levels in freeroam mode (without creating
    a Scenario object), check loading status, and return to the main menu safely.

    Args:
        beamng: An instance of the simulator.
    """

    def __init__(self, beamng):
        """
        Initialize FreeroamApi.

        Args:
            beamng: BeamNG instance
        """
        self.beamng = beamng
        self._wrapper = FreeroamWrapper(beamng)

    def load(self, level_name: str, timeout: float = 120) -> None:
        """
        Load a level in freeroam mode and wait for completion.

        This method:
        1. Safely returns to menu if a level is already loaded
        2. Sends the freeroam load command
        3. Polls until the level is fully loaded

        Args:
            level_name: Level folder name (e.g. 'italy', 'west_coast_usa')
            timeout: Maximum wait time in seconds (default 120)

        Raises:
            TimeoutError: If the level doesn't load within timeout
            RuntimeError: If the load command fails
        """
        logger.info(f"Loading freeroam level: {level_name}")

        # Safe return to menu first (no-op if already in menu)
        self._wrapper.safe_return_to_menu()

        # Send the freeroam load command
        self._wrapper.start_freeroam(level_name)

        # Wait for the level to finish loading
        self._wrapper.wait_for_level_load(level_name, timeout=timeout)

        logger.info(f"Freeroam level '{level_name}' loaded successfully")

    def stop(self) -> None:
        """
        Stop the freeroam session and return to the main menu.

        Safe to call even if already in the menu.
        """
        logger.info("Stopping freeroam session")
        self._wrapper.safe_return_to_menu()

    def is_loaded(self) -> bool:
        """
        Check if a level is currently loaded (freeroam or scenario).

        Returns:
            True if a level is loaded, False if in main menu
        """
        state = self._wrapper.get_gamestate()
        return state == "scenario"

    def get_loaded_level(self) -> str:
        """
        Get the path of the currently loaded level.

        Returns:
            Level path string or empty string if no level is loaded
        """
        return self._wrapper.get_mission_filename()
