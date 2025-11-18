"""
State machine for elevator bot navigation.
Manages different states: searching, approaching, in_elevator, waiting, exiting.
"""

from enum import Enum, auto
from typing import Optional, Dict, Any
import time
import logging

logger = logging.getLogger(__name__)


class BotState(Enum):
    """Possible states for the elevator bot."""
    IDLE = auto()
    SEARCHING_ELEVATOR = auto()
    APPROACHING_ELEVATOR = auto()
    ENTERING_ELEVATOR = auto()
    IN_ELEVATOR = auto()
    WAITING_IN_ELEVATOR = auto()
    PLAYER_DETECTED = auto()
    EXITING_ELEVATOR = auto()
    NAVIGATING_FLOOR = auto()
    ERROR = auto()


class StateMachine:
    """Manages bot state transitions and state-specific logic."""

    def __init__(self, max_state_time: float = 30.0,
                 confirmation_frames: int = 3):
        """
        Initialize state machine.

        Args:
            max_state_time: Maximum time to stay in a state before timeout
            confirmation_frames: Number of consecutive detections needed to confirm
        """
        self.current_state = BotState.IDLE
        self.previous_state = None
        self.state_enter_time = time.time()
        self.max_state_time = max_state_time
        self.confirmation_frames = confirmation_frames
        self.confirmation_counter = {}
        self.state_data: Dict[str, Any] = {}

    def transition_to(self, new_state: BotState, reason: str = ""):
        """
        Transition to a new state.

        Args:
            new_state: State to transition to
            reason: Optional reason for transition (for logging)
        """
        if new_state != self.current_state:
            logger.info(f"State transition: {self.current_state.name} -> {new_state.name}"
                       + (f" ({reason})" if reason else ""))
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_enter_time = time.time()
            self.state_data.clear()

    def confirm_state(self, state: BotState) -> bool:
        """
        Confirm a state detection by requiring multiple consecutive frames.

        Args:
            state: State to confirm

        Returns:
            True if state is confirmed (reached threshold)
        """
        if state not in self.confirmation_counter:
            self.confirmation_counter[state] = 0

        self.confirmation_counter[state] += 1

        # Reset counters for other states
        for s in self.confirmation_counter:
            if s != state:
                self.confirmation_counter[s] = 0

        confirmed = self.confirmation_counter[state] >= self.confirmation_frames

        if confirmed:
            logger.debug(f"State {state.name} confirmed after {self.confirmation_counter[state]} frames")

        return confirmed

    def get_time_in_state(self) -> float:
        """Get how long we've been in the current state."""
        return time.time() - self.state_enter_time

    def is_state_timeout(self) -> bool:
        """Check if current state has exceeded maximum time."""
        return self.get_time_in_state() > self.max_state_time

    def get_current_state(self) -> BotState:
        """Get the current state."""
        return self.current_state

    def get_previous_state(self) -> Optional[BotState]:
        """Get the previous state."""
        return self.previous_state

    def set_state_data(self, key: str, value: Any):
        """Store data associated with current state."""
        self.state_data[key] = value

    def get_state_data(self, key: str, default: Any = None) -> Any:
        """Retrieve data associated with current state."""
        return self.state_data.get(key, default)

    def reset(self):
        """Reset state machine to idle."""
        self.transition_to(BotState.IDLE, "reset")
        self.confirmation_counter.clear()
        self.state_data.clear()

    def get_state_description(self) -> str:
        """Get human-readable description of current state."""
        descriptions = {
            BotState.IDLE: "Waiting for commands",
            BotState.SEARCHING_ELEVATOR: "Looking for elevator",
            BotState.APPROACHING_ELEVATOR: "Moving towards elevator",
            BotState.ENTERING_ELEVATOR: "Entering elevator",
            BotState.IN_ELEVATOR: "Inside elevator",
            BotState.WAITING_IN_ELEVATOR: "Waiting in elevator for players",
            BotState.PLAYER_DETECTED: "Other player detected in elevator",
            BotState.EXITING_ELEVATOR: "Leaving elevator",
            BotState.NAVIGATING_FLOOR: "Navigating floor/path",
            BotState.ERROR: "Error state - needs intervention"
        }
        return descriptions.get(self.current_state, "Unknown state")


class ElevatorStateDetector:
    """Detects game states specific to elevator operation."""

    def __init__(self, vision_detector):
        """
        Initialize state detector.

        Args:
            vision_detector: VisionDetector instance
        """
        self.vision = vision_detector

    def detect_elevator_prompt(self, screen: Any) -> bool:
        """
        Detect if elevator interaction prompt is visible.

        Args:
            screen: Screen capture image

        Returns:
            True if elevator prompt detected
        """
        result = self.vision.detect_ui_element_by_color(screen, 'elevator_prompt')
        return result.detected

    def detect_in_elevator(self, screen: Any) -> bool:
        """
        Detect if player is inside elevator.
        This checks for UI elements specific to being in an elevator.

        Args:
            screen: Screen capture image

        Returns:
            True if inside elevator
        """
        # Check for floor indicator UI
        result = self.vision.detect_ui_element_by_color(screen, 'floor_indicator')
        return result.detected

    def detect_other_players(self, screen: Any) -> bool:
        """
        Detect if other players are present.

        Args:
            screen: Screen capture image

        Returns:
            True if other players detected
        """
        result = self.vision.detect_ui_element_by_color(screen, 'player_tag')
        return result.detected

    def detect_floor_number(self, screen: Any) -> Optional[str]:
        """
        Attempt to detect current floor number.

        Args:
            screen: Screen capture image

        Returns:
            Floor number as string, or None if not detected
        """
        # This would require OCR implementation
        # For now, return None
        # TODO: Integrate pytesseract for OCR
        return None
