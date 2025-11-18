"""
Setup script for Division 2 Elevator Bot.
Helps with initial configuration and dependency checking.
"""

import sys
import subprocess
import platform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8 or higher is required!")
        return False

    logger.info("✓ Python version is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    logger.info("Installing dependencies from requirements.txt...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")

    required = [
        'cv2',
        'numpy',
        'PIL',
        'mss',
        'yaml',
        'keyboard'
    ]

    missing = []

    for module in required:
        try:
            __import__(module)
            logger.info(f"✓ {module}")
        except ImportError:
            logger.warning(f"✗ {module} not found")
            missing.append(module)

    if missing:
        logger.warning(f"Missing modules: {', '.join(missing)}")
        return False

    logger.info("✓ All dependencies are installed")
    return True


def check_platform():
    """Check platform and provide relevant info."""
    system = platform.system()
    logger.info(f"Platform: {system}")

    if system == "Windows":
        logger.info("✓ Windows detected - full support")
        logger.info("  Make sure to run as Administrator for input simulation")
    elif system == "Linux":
        logger.info("⚠ Linux detected - experimental support")
        logger.info("  You may need to run with sudo for input simulation")
    elif system == "Darwin":
        logger.info("⚠ macOS detected - experimental support")
        logger.info("  Input simulation may require additional permissions")
    else:
        logger.warning(f"⚠ Unknown platform: {system}")

    return True


def create_directories():
    """Create necessary directories."""
    import os

    dirs = ['debug_screenshots', 'logs']

    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"✓ Created directory: {dir_name}")
        else:
            logger.info(f"✓ Directory exists: {dir_name}")

    return True


def run_tests():
    """Run basic tests to verify setup."""
    logger.info("\nRunning basic tests...")

    try:
        # Test screen capture
        from screen_capture import ScreenCapture
        screen = ScreenCapture()
        img = screen.capture()
        screen.cleanup()
        logger.info(f"✓ Screen capture working ({img.shape})")

        # Test vision detector
        from vision_detector import VisionDetector
        vision = VisionDetector()
        logger.info("✓ Vision detector initialized")

        return True
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("Division 2 Elevator Bot - Setup")
    logger.info("=" * 60)
    logger.info("")

    success = True

    # Check Python version
    if not check_python_version():
        success = False

    # Check platform
    check_platform()

    # Check/install dependencies
    if not check_dependencies():
        logger.info("\nAttempting to install missing dependencies...")
        if not install_dependencies():
            success = False
        else:
            # Check again after installation
            if not check_dependencies():
                success = False

    # Create directories
    if not create_directories():
        success = False

    # Run tests
    if success:
        if not run_tests():
            logger.warning("Some tests failed, but you can still try running the bot")

    logger.info("")
    logger.info("=" * 60)

    if success:
        logger.info("✓ Setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Review config.yaml and adjust key bindings")
        logger.info("2. Start The Division 2")
        logger.info("3. Run: python main.py")
        logger.info("")
        logger.info("For detailed instructions, see QUICKSTART.md")
    else:
        logger.error("✗ Setup encountered errors")
        logger.error("Please fix the errors above and try again")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
