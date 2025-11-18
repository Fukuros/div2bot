"""
Vision detection module using OpenCV for game state recognition.
Detects elevators, UI elements, players, and other game features.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of a vision detection operation."""
    detected: bool
    confidence: float
    location: Optional[Tuple[int, int]] = None
    region: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h


class VisionDetector:
    """Computer vision detector for Division 2 game elements."""

    def __init__(self, template_threshold: float = 0.7):
        """
        Initialize vision detector.

        Args:
            template_threshold: Minimum confidence for template matching
        """
        self.template_threshold = template_threshold
        self.templates = {}

    def detect_template(self, image: np.ndarray, template: np.ndarray,
                       threshold: Optional[float] = None) -> DetectionResult:
        """
        Detect a template image within a larger image.

        Args:
            image: Source image to search in
            template: Template image to find
            threshold: Custom threshold (uses default if None)

        Returns:
            DetectionResult with detection information
        """
        if threshold is None:
            threshold = self.template_threshold

        # Convert to grayscale for better matching
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        detected = max_val >= threshold

        if detected:
            h, w = gray_template.shape
            return DetectionResult(
                detected=True,
                confidence=max_val,
                location=max_loc,
                region=(max_loc[0], max_loc[1], w, h)
            )
        else:
            return DetectionResult(detected=False, confidence=max_val)

    def detect_color_region(self, image: np.ndarray,
                           lower_color: np.ndarray,
                           upper_color: np.ndarray,
                           min_area: int = 100) -> DetectionResult:
        """
        Detect regions of a specific color range.

        Args:
            image: Source image
            lower_color: Lower HSV color bound
            upper_color: Upper HSV color bound
            min_area: Minimum area in pixels to consider

        Returns:
            DetectionResult with detection information
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create mask for color range
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return DetectionResult(detected=False, confidence=0.0)

        # Find largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area < min_area:
            return DetectionResult(detected=False, confidence=0.0)

        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate confidence based on area
        image_area = image.shape[0] * image.shape[1]
        confidence = min(1.0, area / (image_area * 0.1))

        return DetectionResult(
            detected=True,
            confidence=confidence,
            location=(x + w//2, y + h//2),
            region=(x, y, w, h)
        )

    def detect_ui_element_by_color(self, image: np.ndarray,
                                   element_name: str) -> DetectionResult:
        """
        Detect common UI elements by their characteristic colors.

        Args:
            image: Source image
            element_name: Name of UI element ('elevator_prompt', 'floor_indicator', etc.)

        Returns:
            DetectionResult
        """
        # Define color ranges for common Division 2 UI elements (in HSV)
        ui_colors = {
            # Orange/yellow interaction prompt (F to interact)
            'elevator_prompt': {
                'lower': np.array([10, 100, 100]),
                'upper': np.array([30, 255, 255])
            },
            # White/light gray UI elements
            'floor_indicator': {
                'lower': np.array([0, 0, 200]),
                'upper': np.array([180, 30, 255])
            },
            # Player name tags (typically white/blue)
            'player_tag': {
                'lower': np.array([90, 50, 150]),
                'upper': np.array([130, 255, 255])
            }
        }

        if element_name not in ui_colors:
            logger.warning(f"Unknown UI element: {element_name}")
            return DetectionResult(detected=False, confidence=0.0)

        colors = ui_colors[element_name]
        return self.detect_color_region(image, colors['lower'], colors['upper'])

    def detect_text_region(self, image: np.ndarray,
                          expected_texts: List[str] = None) -> DetectionResult:
        """
        Detect text regions in the image.
        Note: For better accuracy, consider integrating OCR (pytesseract)

        Args:
            image: Source image
            expected_texts: Optional list of expected text strings

        Returns:
            DetectionResult indicating if text was found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Find contours that might be text
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by aspect ratio (text-like)
        text_contours = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h) if h > 0 else 0
            if 0.1 < aspect_ratio < 10 and w > 10 and h > 10:
                text_contours.append(cnt)

        if text_contours:
            # Get bounding box of all text regions
            all_points = np.concatenate(text_contours)
            x, y, w, h = cv2.boundingRect(all_points)

            return DetectionResult(
                detected=True,
                confidence=0.8,
                location=(x + w//2, y + h//2),
                region=(x, y, w, h)
            )

        return DetectionResult(detected=False, confidence=0.0)

    def detect_movement_indicators(self, prev_frame: np.ndarray,
                                   curr_frame: np.ndarray,
                                   threshold: int = 30) -> bool:
        """
        Detect if significant movement is occurring in the scene.

        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
            threshold: Motion detection threshold

        Returns:
            True if movement detected
        """
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(prev_gray, curr_gray)

        # Threshold the difference
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        # Calculate percentage of changed pixels
        changed_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        change_percentage = changed_pixels / total_pixels

        # Consider it movement if more than 5% of pixels changed
        return change_percentage > 0.05

    def load_template(self, name: str, image_path: str):
        """
        Load a template image for later use.

        Args:
            name: Name to reference this template
            image_path: Path to template image file
        """
        template = cv2.imread(image_path)
        if template is not None:
            self.templates[name] = template
            logger.info(f"Loaded template '{name}' from {image_path}")
        else:
            logger.error(f"Failed to load template from {image_path}")

    def detect_loaded_template(self, image: np.ndarray,
                              template_name: str) -> DetectionResult:
        """
        Detect a previously loaded template.

        Args:
            image: Source image
            template_name: Name of loaded template

        Returns:
            DetectionResult
        """
        if template_name not in self.templates:
            logger.error(f"Template '{template_name}' not loaded")
            return DetectionResult(detected=False, confidence=0.0)

        return self.detect_template(image, self.templates[template_name])
