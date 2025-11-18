"""
Dependency checker for Division 2 Elevator Bot.
Verifies all required software is installed and properly configured.
"""

import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    logger.info(f"✓ Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("✗ Python 3.8 or higher is required!")
        return False

    return True


def check_python_packages():
    """Check if all required Python packages are installed."""
    required_packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('PIL', 'pillow'),
        ('mss', 'mss'),
        ('yaml', 'pyyaml'),
    ]

    optional_packages = [
        ('pytesseract', 'pytesseract'),
        ('pydirectinput', 'pydirectinput'),
        ('keyboard', 'keyboard'),
    ]

    all_ok = True

    logger.info("\nChecking required Python packages:")
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            logger.info(f"  ✓ {package_name}")
        except ImportError:
            logger.error(f"  ✗ {package_name} - Install with: pip install {package_name}")
            all_ok = False

    logger.info("\nChecking optional Python packages:")
    for module_name, package_name in optional_packages:
        try:
            __import__(module_name)
            logger.info(f"  ✓ {package_name}")
        except ImportError:
            logger.warning(f"  ! {package_name} - Install with: pip install {package_name}")
            if module_name == 'pytesseract':
                logger.warning("    NOTE: pytesseract is CRITICAL for HUD text recognition!")
                logger.warning("    Without it, the bot will use unreliable color detection.")

    return all_ok


def check_tesseract_ocr():
    """Check if Tesseract OCR is installed and accessible."""
    logger.info("\nChecking Tesseract OCR:")

    try:
        import pytesseract

        # Try to get Tesseract version
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"  ✓ Tesseract OCR v{version} found")
            return True
        except Exception as e:
            logger.error(f"  ✗ pytesseract installed but Tesseract executable not found")
            logger.error(f"    Error: {e}")
            logger.error("\n    SOLUTION:")
            logger.error("    1. Download Tesseract installer from:")
            logger.error("       https://github.com/UB-Mannheim/tesseract/wiki")
            logger.error("    2. Install it (default location: C:\\Program Files\\Tesseract-OCR)")
            logger.error("    3. Add to PATH or set in Python:")
            logger.error("       pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
            return False

    except ImportError:
        logger.error("  ✗ pytesseract not installed")
        logger.error("    Install with: pip install pytesseract")
        logger.error("    Then install Tesseract OCR from:")
        logger.error("    https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def test_screen_capture():
    """Test if screen capture works."""
    logger.info("\nTesting screen capture:")

    try:
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            img = sct.grab(monitor)
            logger.info(f"  ✓ Screen capture working ({monitor['width']}x{monitor['height']})")
            return True
    except Exception as e:
        logger.error(f"  ✗ Screen capture failed: {e}")
        return False


def main():
    """Run all checks."""
    logger.info("=" * 60)
    logger.info("Division 2 Elevator Bot - Dependency Checker")
    logger.info("=" * 60)

    all_ok = True

    # Check Python version
    if not check_python_version():
        all_ok = False

    # Check Python packages
    if not check_python_packages():
        all_ok = False

    # Check Tesseract OCR (critical!)
    tesseract_ok = check_tesseract_ocr()
    if not tesseract_ok:
        logger.warning("\n⚠️  WARNING: Tesseract OCR not available!")
        logger.warning("The bot will work but will use UNRELIABLE color detection.")
        logger.warning("You will experience false positives and incorrect state detection.")
        logger.warning("\nFor best results, install Tesseract OCR!")

    # Test screen capture
    if not test_screen_capture():
        all_ok = False

    # Summary
    logger.info("\n" + "=" * 60)
    if all_ok and tesseract_ok:
        logger.info("✓ All dependencies satisfied - Ready to run!")
        logger.info("\nRun the bot with: python main.py")
    elif all_ok:
        logger.warning("⚠️  Core dependencies OK but Tesseract OCR missing")
        logger.warning("Bot will work with reduced accuracy")
        logger.warning("\nRun the bot with: python main.py")
    else:
        logger.error("✗ Some dependencies are missing")
        logger.error("Please install missing packages and try again")
        return 1

    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
