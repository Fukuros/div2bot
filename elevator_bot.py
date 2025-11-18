"""
Main elevator bot logic for Division 2.
Automates elevator usage for accessibility purposes.
"""

import time
import cv2
import logging
from typing import Optional
import numpy as np

from screen_capture import ScreenCapture
from vision_detector import VisionDetector
from state_machine import StateMachine, BotState, ElevatorStateDetector
from input_controller import InputController

logger = logging.getLogger(__name__)


class ElevatorBot:
    """
    Main bot class that coordinates all components.
    Handles the complete elevator automation workflow.
    """

    def __init__(self, config: dict):
        """
        Initialize elevator bot.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.running = False

        # Initialize components
        self.screen = ScreenCapture()
        self.vision = VisionDetector(
            template_threshold=config['detection']['template_threshold']
        )
        self.state_machine = StateMachine(
            max_state_time=config['states']['max_state_time'],
            confirmation_frames=config['states']['confirmation_frames']
        )
        self.state_detector = ElevatorStateDetector(self.vision)
        self.input = InputController(config['keybinds'])

        # Bot settings
        self.capture_interval = config['detection']['capture_interval']
        self.elevator_wait_time = config['movement']['elevator_wait_time']
        self.action_delay = config['movement']['action_delay']
        self.debug_enabled = config['debug']['enabled']

        # Frame tracking for movement detection
        self.previous_frame: Optional[np.ndarray] = None

        logger.info("Elevator bot initialized")
        logger.info(f"Resolution: {self.screen.get_resolution()}")

    def start(self):
        """Start the bot main loop."""
        logger.info("Starting elevator bot...")
        self.running = True
        self.state_machine.transition_to(BotState.SEARCHING_ELEVATOR, "bot started")

        try:
            while self.running:
                self.update()
                time.sleep(self.capture_interval)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """Stop the bot and cleanup."""
        logger.info("Stopping bot...")
        self.running = False
        self.input.emergency_stop()
        self.screen.cleanup()

    def update(self):
        """Main update loop - called every frame."""
        # Capture screen
        screen = self.screen.capture()

        # Check for state timeout
        if self.state_machine.is_state_timeout():
            logger.warning(f"State timeout in {self.state_machine.get_current_state().name}")
            self.handle_timeout()
            return

        # Process based on current state
        current_state = self.state_machine.get_current_state()

        if current_state == BotState.SEARCHING_ELEVATOR:
            self.handle_searching_elevator(screen)
        elif current_state == BotState.APPROACHING_ELEVATOR:
            self.handle_approaching_elevator(screen)
        elif current_state == BotState.ENTERING_ELEVATOR:
            self.handle_entering_elevator(screen)
        elif current_state == BotState.IN_ELEVATOR:
            self.handle_in_elevator(screen)
        elif current_state == BotState.WAITING_IN_ELEVATOR:
            self.handle_waiting_in_elevator(screen)
        elif current_state == BotState.PLAYER_DETECTED:
            self.handle_player_detected(screen)
        elif current_state == BotState.EXITING_ELEVATOR:
            self.handle_exiting_elevator(screen)
        elif current_state == BotState.NAVIGATING_FLOOR:
            self.handle_navigating_floor(screen)

        # Store frame for next iteration
        self.previous_frame = screen.copy()

        # Debug visualization
        if self.debug_enabled:
            self.show_debug_info(screen)

    def handle_searching_elevator(self, screen: np.ndarray):
        """Handle SEARCHING_ELEVATOR state."""
        # Look for elevator interaction prompt
        if self.state_detector.detect_elevator_prompt(screen):
            if self.state_machine.confirm_state(BotState.APPROACHING_ELEVATOR):
                self.state_machine.transition_to(
                    BotState.APPROACHING_ELEVATOR,
                    "elevator prompt detected"
                )
        else:
            # Keep searching - could add simple movement pattern here
            logger.debug("Searching for elevator...")

    def handle_approaching_elevator(self, screen: np.ndarray):
        """Handle APPROACHING_ELEVATOR state."""
        # Check if still seeing elevator prompt
        if self.state_detector.detect_elevator_prompt(screen):
            # Move towards elevator
            move_duration = self.config['movement']['move_duration']
            self.input.move_to_elevator(move_duration)

            # Transition to entering
            self.state_machine.transition_to(
                BotState.ENTERING_ELEVATOR,
                "approaching elevator"
            )
            time.sleep(self.action_delay)
        else:
            # Lost sight of elevator
            self.state_machine.transition_to(
                BotState.SEARCHING_ELEVATOR,
                "lost elevator prompt"
            )

    def handle_entering_elevator(self, screen: np.ndarray):
        """Handle ENTERING_ELEVATOR state."""
        # Press interact key to enter elevator
        self.input.enter_elevator()

        # Wait a bit for the interaction to complete
        time.sleep(1.0)

        # Check if we're now in elevator
        if self.state_detector.detect_in_elevator(screen):
            self.state_machine.transition_to(
                BotState.IN_ELEVATOR,
                "successfully entered elevator"
            )
        else:
            # Try again or go back to searching
            retry_count = self.state_machine.get_state_data('retry_count', 0)
            if retry_count < 3:
                self.state_machine.set_state_data('retry_count', retry_count + 1)
                logger.info(f"Retrying elevator entry (attempt {retry_count + 1})")
                self.state_machine.transition_to(
                    BotState.APPROACHING_ELEVATOR,
                    "retry entry"
                )
            else:
                logger.warning("Failed to enter elevator after 3 attempts")
                self.state_machine.transition_to(
                    BotState.SEARCHING_ELEVATOR,
                    "entry failed"
                )

    def handle_in_elevator(self, screen: np.ndarray):
        """Handle IN_ELEVATOR state."""
        # Confirm we're in the elevator
        if self.state_detector.detect_in_elevator(screen):
            # Transition to waiting state
            self.state_machine.transition_to(
                BotState.WAITING_IN_ELEVATOR,
                "confirmed in elevator"
            )
            self.state_machine.set_state_data('wait_start_time', time.time())
        else:
            # We're not actually in the elevator
            logger.warning("Not detected in elevator, going back to search")
            self.state_machine.transition_to(
                BotState.SEARCHING_ELEVATOR,
                "not in elevator"
            )

    def handle_waiting_in_elevator(self, screen: np.ndarray):
        """Handle WAITING_IN_ELEVATOR state."""
        # Check for other players
        if self.state_detector.detect_other_players(screen):
            if self.state_machine.confirm_state(BotState.PLAYER_DETECTED):
                self.state_machine.transition_to(
                    BotState.PLAYER_DETECTED,
                    "player joined elevator"
                )
                return

        # Check if we've waited long enough
        wait_start = self.state_machine.get_state_data('wait_start_time', time.time())
        elapsed = time.time() - wait_start

        if elapsed < self.elevator_wait_time:
            logger.debug(f"Waiting in elevator... {elapsed:.1f}/{self.elevator_wait_time}s")
        else:
            # Waited long enough, can continue to summit
            logger.info("Wait time complete, continuing to summit")
            # Here you would add summit button press logic
            # For now, just stay in elevator
            pass

    def handle_player_detected(self, screen: np.ndarray):
        """Handle PLAYER_DETECTED state."""
        logger.info("Player detected in elevator - leaving group")

        # Use /leave command to exit the elevator group
        self.input.leave_group()

        # Wait for the command to process
        time.sleep(1.0)

        # Transition to exiting state
        self.state_machine.transition_to(
            BotState.EXITING_ELEVATOR,
            "leaving due to player presence"
        )

    def handle_exiting_elevator(self, screen: np.ndarray):
        """Handle EXITING_ELEVATOR state."""
        logger.info("Exiting elevator...")

        # Move out of elevator
        self.input.exit_elevator()

        # Wait for exit animation
        exit_delay = self.config['movement']['exit_delay']
        time.sleep(exit_delay)

        # Check if we successfully exited
        if not self.state_detector.detect_in_elevator(screen):
            logger.info("Successfully exited elevator")
            # Return to searching for next cycle
            self.state_machine.transition_to(
                BotState.SEARCHING_ELEVATOR,
                "exited elevator"
            )
        else:
            # Still in elevator, try /leave command again
            logger.warning("Still in elevator, trying /leave command again")
            self.input.leave_group()
            time.sleep(1.0)

    def handle_navigating_floor(self, screen: np.ndarray):
        """Handle NAVIGATING_FLOOR state."""
        # This state handles floor/path navigation
        # Could be expanded with waypoint system
        logger.debug("Navigating floor...")

        # For now, just search for elevator again
        self.state_machine.transition_to(
            BotState.SEARCHING_ELEVATOR,
            "navigation complete"
        )

    def handle_timeout(self):
        """Handle state timeout."""
        logger.warning("Handling state timeout")
        self.input.emergency_stop()

        # Reset to searching state
        self.state_machine.transition_to(
            BotState.SEARCHING_ELEVATOR,
            "timeout recovery"
        )

    def show_debug_info(self, screen: np.ndarray):
        """Show debug visualization."""
        # Create a copy for visualization
        debug_frame = screen.copy()

        # Add text overlay with state info
        state_text = self.state_machine.get_state_description()
        time_in_state = self.state_machine.get_time_in_state()

        cv2.putText(
            debug_frame,
            f"State: {state_text}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            debug_frame,
            f"Time: {time_in_state:.1f}s",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Resize for display if needed
        height, width = debug_frame.shape[:2]
        if width > 1280:
            scale = 1280 / width
            new_width = 1280
            new_height = int(height * scale)
            debug_frame = cv2.resize(debug_frame, (new_width, new_height))

        cv2.imshow('Elevator Bot Debug', debug_frame)
        cv2.waitKey(1)

    def get_status(self) -> dict:
        """
        Get current bot status.

        Returns:
            Dictionary with status information
        """
        return {
            'running': self.running,
            'state': self.state_machine.get_current_state().name,
            'state_description': self.state_machine.get_state_description(),
            'time_in_state': self.state_machine.get_time_in_state(),
            'resolution': self.screen.get_resolution()
        }
