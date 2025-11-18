"""
Test script for vision detection functionality.
Run this to test color and template detection.
"""

import cv2
import logging
import numpy as np
from screen_capture import ScreenCapture
from vision_detector import VisionDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test vision detection."""
    logger.info("Testing vision detection...")

    # Initialize components
    screen = ScreenCapture()
    vision = VisionDetector()

    logger.info("Capturing screen...")
    img = screen.capture()

    # Test UI element detection
    logger.info("\n--- Testing UI Element Detection ---")

    elements = ['elevator_prompt', 'floor_indicator', 'player_tag']

    for element in elements:
        result = vision.detect_ui_element_by_color(img, element)
        logger.info(f"{element}: Detected={result.detected}, "
                   f"Confidence={result.confidence:.2f}")

        if result.detected and result.region:
            # Draw rectangle on detection
            x, y, w, h = result.region
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, element, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Test text detection
    logger.info("\n--- Testing Text Detection ---")
    text_result = vision.detect_text_region(img)
    logger.info(f"Text detected: {text_result.detected}, "
               f"Confidence={text_result.confidence:.2f}")

    if text_result.detected and text_result.region:
        x, y, w, h = text_result.region
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(img, "TEXT", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display results
    logger.info("\n--- Displaying Results ---")
    logger.info("Green boxes: UI elements")
    logger.info("Blue boxes: Text regions")
    logger.info("Press any key to close...")

    # Resize if too large
    display_img = img.copy()
    if display_img.shape[1] > 1280:
        scale = 1280 / display_img.shape[1]
        new_width = 1280
        new_height = int(display_img.shape[0] * scale)
        display_img = cv2.resize(display_img, (new_width, new_height))

    cv2.imshow('Detection Test', display_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Cleanup
    screen.cleanup()

    logger.info("\nDetection test complete!")
    logger.info("\nTips:")
    logger.info("- If no elements detected, adjust thresholds in config.yaml")
    logger.info("- Make sure The Division 2 is running and visible")
    logger.info("- Try standing near an elevator or UI elements")


if __name__ == "__main__":
    main()
