"""
Input controller for simulating keyboard and mouse input.
Works cross-platform with fallback mechanisms.
"""

import time
import logging
import platform
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import platform-specific modules
try:
    if platform.system() == "Windows":
        import pydirectinput
        USE_PYDIRECTINPUT = True
    else:
        import keyboard
        USE_PYDIRECTINPUT = False
except ImportError:
    logger.warning("Could not import input libraries, will use keyboard module")
    import keyboard
    USE_PYDIRECTINPUT = False


class InputController:
    """Handles keyboard and mouse input simulation."""

    def __init__(self, key_bindings: dict):
        """
        Initialize input controller.

        Args:
            key_bindings: Dictionary of action -> key mappings
        """
        self.keys = key_bindings
        self.use_pydirectinput = USE_PYDIRECTINPUT and platform.system() == "Windows"

        if self.use_pydirectinput:
            logger.info("Using pydirectinput for input simulation")
            # Set pydirectinput to be faster
            pydirectinput.PAUSE = 0.05
        else:
            logger.info("Using keyboard module for input simulation")

    def press_key(self, key: str, duration: float = 0.1):
        """
        Press and release a key.

        Args:
            key: Key to press
            duration: How long to hold the key (seconds)
        """
        try:
            if self.use_pydirectinput:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
            else:
                keyboard.press(key)
                time.sleep(duration)
                keyboard.release(key)

            logger.debug(f"Pressed key: {key} for {duration}s")
        except Exception as e:
            logger.error(f"Error pressing key {key}: {e}")

    def hold_key(self, key: str):
        """
        Hold down a key.

        Args:
            key: Key to hold
        """
        try:
            if self.use_pydirectinput:
                pydirectinput.keyDown(key)
            else:
                keyboard.press(key)
        except Exception as e:
            logger.error(f"Error holding key {key}: {e}")

    def release_key(self, key: str):
        """
        Release a held key.

        Args:
            key: Key to release
        """
        try:
            if self.use_pydirectinput:
                pydirectinput.keyUp(key)
            else:
                keyboard.release(key)
        except Exception as e:
            logger.error(f"Error releasing key {key}: {e}")

    def move_forward(self, duration: float = 0.5):
        """Move forward for specified duration."""
        self.press_key(self.keys.get('forward', 'w'), duration)

    def move_backward(self, duration: float = 0.5):
        """Move backward for specified duration."""
        self.press_key(self.keys.get('backward', 's'), duration)

    def move_left(self, duration: float = 0.5):
        """Move left for specified duration."""
        self.press_key(self.keys.get('left', 'a'), duration)

    def move_right(self, duration: float = 0.5):
        """Move right for specified duration."""
        self.press_key(self.keys.get('right', 'd'), duration)

    def interact(self, duration: float = 0.2):
        """Press interact key."""
        self.press_key(self.keys.get('interact', 'f'), duration)

    def sprint(self, enable: bool = True):
        """Enable or disable sprinting."""
        sprint_key = self.keys.get('sprint', 'shift')
        if enable:
            self.hold_key(sprint_key)
        else:
            self.release_key(sprint_key)

    def move_to_elevator(self, duration: float = 2.0):
        """
        Simple forward movement towards elevator.

        Args:
            duration: How long to move forward
        """
        logger.info(f"Moving towards elevator for {duration}s")
        self.sprint(True)
        time.sleep(0.1)
        self.move_forward(duration)
        self.sprint(False)

    def enter_elevator(self):
        """Interact with elevator to enter."""
        logger.info("Attempting to enter elevator")
        self.interact(0.3)
        time.sleep(0.5)

    def exit_elevator(self):
        """Exit elevator by moving forward."""
        logger.info("Exiting elevator")
        self.move_forward(2.0)
        time.sleep(0.5)

    def wait(self, duration: float):
        """
        Wait for specified duration.

        Args:
            duration: Time to wait in seconds
        """
        time.sleep(duration)

    def open_chat(self):
        """Open the chat window."""
        chat_key = self.keys.get('chat', 'enter')
        self.press_key(chat_key, 0.1)
        time.sleep(0.3)  # Wait for chat to open

    def type_text(self, text: str, delay: float = 0.05):
        """
        Type text character by character.

        Args:
            text: Text to type
            delay: Delay between characters
        """
        logger.debug(f"Typing: {text}")

        for char in text:
            try:
                if self.use_pydirectinput:
                    pydirectinput.press(char)
                else:
                    keyboard.write(char, delay=0)
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Error typing character '{char}': {e}")

    def send_chat_command(self, command: str):
        """
        Send a command in the game chat.

        Args:
            command: Command to send (e.g., "/leave")
        """
        logger.info(f"Sending chat command: {command}")

        # Open chat
        self.open_chat()

        # Type the command
        self.type_text(command)

        # Press enter to send
        chat_key = self.keys.get('chat', 'enter')
        self.press_key(chat_key, 0.1)

        # Wait for command to process
        time.sleep(0.5)

    def leave_group(self):
        """Leave the current group using /leave command."""
        logger.info("Leaving group via /leave command")
        self.send_chat_command("/leave")

    def emergency_stop(self):
        """Release all keys."""
        logger.info("Emergency stop - releasing all keys")
        common_keys = ['w', 'a', 's', 'd', 'shift', 'ctrl', 'space']

        for key in common_keys:
            try:
                self.release_key(key)
            except:
                pass
