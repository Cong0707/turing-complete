"""Sprite-safe, short-path routing."""

from .astar import FanoutTrackCapacityError, RoutedEdge, RoutingResult, route

__all__ = ["FanoutTrackCapacityError", "RoutedEdge", "RoutingResult", "route"]
