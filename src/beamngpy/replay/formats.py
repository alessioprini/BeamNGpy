"""
Format handlers for replay data serialization and deserialization.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class ReplayFormat:
    """Base class for replay format handlers."""

    @staticmethod
    def save(data: Dict[str, Any], filepath: str) -> None:
        """Save replay data to file."""
        raise NotImplementedError

    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        """Load replay data from file."""
        raise NotImplementedError


class JSONReplayFormat(ReplayFormat):
    """JSON-based replay format handler."""

    @staticmethod
    def save(data: Dict[str, Any], filepath: str) -> None:
        """
        Save replay data to JSON file.

        Args:
            data: Replay data dictionary containing metadata and frames
            filepath: Path to save the JSON file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        """
        Load replay data from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            Dictionary containing replay metadata and frames
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Replay file not found: {filepath}")

        with open(filepath, 'r') as f:
            return json.load(f)


class ReplayMetadata:
    """Container for replay metadata."""

    def __init__(self):
        self.version = "1.0"
        self.format = "json"
        self.scenario: str = ""
        self.duration: float = 0.0
        self.frame_count: int = 0
        self.frame_rate: float = 60.0
        self.creation_time: str = ""
        self.description: str = ""
        self.custom_data: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "version": self.version,
            "format": self.format,
            "scenario": self.scenario,
            "duration": self.duration,
            "frame_count": self.frame_count,
            "frame_rate": self.frame_rate,
            "creation_time": self.creation_time,
            "description": self.description,
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayMetadata":
        """Create metadata from dictionary."""
        metadata = cls()
        metadata.version = data.get("version", "1.0")
        metadata.format = data.get("format", "json")
        metadata.scenario = data.get("scenario", "")
        metadata.duration = data.get("duration", 0.0)
        metadata.frame_count = data.get("frame_count", 0)
        metadata.frame_rate = data.get("frame_rate", 60.0)
        metadata.creation_time = data.get("creation_time", "")
        metadata.description = data.get("description", "")
        metadata.custom_data = data.get("custom_data", {})
        return metadata


class ReplayFrame:
    """Container for a single replay frame."""

    def __init__(self, timestamp: float, lua_state: Dict[str, Any]):
        """
        Initialize a replay frame.

        Args:
            timestamp: Frame timestamp in seconds
            lua_state: Lua state dictionary containing simulation snapshot
        """
        self.timestamp = timestamp
        self.lua_state = lua_state

    def to_dict(self) -> Dict[str, Any]:
        """Convert frame to dictionary."""
        return {
            "timestamp": self.timestamp,
            "lua_state": self.lua_state,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayFrame":
        """Create frame from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            lua_state=data["lua_state"],
        )
