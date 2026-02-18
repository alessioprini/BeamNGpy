"""
Freeroam functionality for BeamNGpy.

This module provides freeroam level loading capabilities by leveraging BeamNG's
freeroam_freeroam Lua extension through queue_lua_command.
"""

from .freeroam_wrapper import FreeroamWrapper

__all__ = ["FreeroamWrapper"]
