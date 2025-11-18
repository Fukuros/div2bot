"""
Test script for screen capture functionality.
Run this to verify screen capture is working correctly.
"""

import cv2
import logging
from screen_capture import ScreenCapture

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test screen capture."""
    logger.info("Testing screen capture...")

    # Initialize screen capture
    screen = ScreenCapture()
    resolution = screen.get_resolution()

    logger.info(f"Screen resolution: {resolution[0]}x{resolution[1]}")

    # Capture full screen
    logger.info("Capturing full screen...")
    img = screen.capture()
    logger.info(f"Captured image shape: {img.shape}")

    # Test region capture with percentages
    logger.info("Capturing center region (50%, 50%, 25%, 25%)...")
    center_region = screen.capture_region_percent(0.375, 0.375, 0.25, 0.25)
    logger.info(f"Center region shape: {center_region.shape}")

    # Display the captures
    logger.info("Displaying captures (press any key to close)...")

    # Resize if too large
    display_img = img.copy()
    if display_img.shape[1] > 1280:
        scale = 1280 / display_img.shape[1]
        new_width = 1280
        new_height = int(display_img.shape[0] * scale)
        display_img = cv2.resize(display_img, (new_width, new_height))

    cv2.imshow('Full Screen Capture', display_img)
    cv2.imshow('Center Region', center_region)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Cleanup
    screen.cleanup()

    logger.info("Screen capture test complete!")


if __name__ == "__main__":
    main()
