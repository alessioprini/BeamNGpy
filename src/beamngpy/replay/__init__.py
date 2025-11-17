"""
Replay functionality for BeamNGpy using core_replay Lua extension.

This module provides high-fidelity replay capabilities by leveraging BeamNG's
native core_replay Lua extension through queue_lua_command, ensuring complete
simulation state (vehicles, traffic, environment) is recorded and replayed accurately.
"""

from .core_replay_wrapper import CoreReplayWrapper

__all__ = ["CoreReplayWrapper"]
