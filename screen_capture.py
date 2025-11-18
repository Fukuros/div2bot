"""
Screen capture module for Division 2 bot.
Works with any resolution, windowed or borderless mode.
"""

import mss
import numpy as np
import cv2
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Handle screen capture operations."""

    def __init__(self, monitor_index: int = 1):
        """
        Initialize screen capture.

        Args:
            monitor_index: Which monitor to capture (1 = primary)
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.monitor = self.sct.monitors[monitor_index]
        self.resolution = (self.monitor['width'], self.monitor['height'])
        logger.info(f"Screen capture initialized at resolution: {self.resolution}")

    def capture(self, region: Optional[dict] = None) -> np.ndarray:
        """
        Capture the screen or a region of it.

        Args:
            region: Optional dict with 'top', 'left', 'width', 'height' keys
                   If None, captures entire monitor

        Returns:
            numpy array in BGR format (OpenCV compatible)
        """
        if region is None:
            capture_area = self.monitor
        else:
            capture_area = {
                'top': region.get('top', 0),
                'left': region.get('left', 0),
                'width': region.get('width', self.monitor['width']),
                'height': region.get('height', self.monitor['height'])
            }

        # Capture screenshot
        screenshot = self.sct.grab(capture_area)

        # Convert to numpy array and BGR format
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

    def get_relative_region(self, x_percent: float, y_percent: float,
                           width_percent: float, height_percent: float) -> dict:
        """
        Get a screen region using percentage-based coordinates.
        This allows resolution-independent region detection.

        Args:
            x_percent: X position as percentage (0.0 to 1.0)
            y_percent: Y position as percentage (0.0 to 1.0)
            width_percent: Width as percentage (0.0 to 1.0)
            height_percent: Height as percentage (0.0 to 1.0)

        Returns:
            Region dictionary
        """
        return {
            'left': int(self.monitor['left'] + self.monitor['width'] * x_percent),
            'top': int(self.monitor['top'] + self.monitor['height'] * y_percent),
            'width': int(self.monitor['width'] * width_percent),
            'height': int(self.monitor['height'] * height_percent)
        }

    def capture_region_percent(self, x: float, y: float,
                              width: float, height: float) -> np.ndarray:
        """
        Capture a region using percentage-based coordinates.

        Args:
            x: X position as percentage (0.0 to 1.0)
            y: Y position as percentage (0.0 to 1.0)
            width: Width as percentage (0.0 to 1.0)
            height: Height as percentage (0.0 to 1.0)

        Returns:
            Captured image as numpy array
        """
        region = self.get_relative_region(x, y, width, height)
        return self.capture(region)

    def get_resolution(self) -> Tuple[int, int]:
        """Get current monitor resolution."""
        return self.resolution

    def cleanup(self):
        """Clean up resources."""
        self.sct.close()
