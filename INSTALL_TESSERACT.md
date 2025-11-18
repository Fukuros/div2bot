# Installing Tesseract OCR

Tesseract OCR is **CRITICAL** for accurate bot operation. Without it, the bot cannot read HUD text and will experience false positives.

## Why You Need It

The bot reads text from your screen like:
- "Enter the elevator 48m"
- "Floor 10"
- "Summit"

Without Tesseract, the bot can only guess based on colors, which is unreliable.

## Windows Installation (Detailed)

### Step 1: Download Tesseract

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Under "Tesseract at UB Mannheim", click the latest installer
   - Usually named like `tesseract-ocr-w64-setup-5.3.3.20231005.exe`
3. Download the installer

### Step 2: Install Tesseract

1. Run the downloaded `.exe` file
2. **IMPORTANT**: During installation, note the installation path
   - Default is: `C:\Program Files\Tesseract-OCR`
3. Complete the installation

### Step 3: Add to PATH (Option A - Recommended)

1. Open Windows Search, type "environment variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables..." button
4. Under "System variables", find and select "Path"
5. Click "Edit..."
6. Click "New"
7. Add: `C:\Program Files\Tesseract-OCR`
8. Click "OK" on all dialogs
9. **RESTART your terminal/command prompt**

### Step 4: Verify Installation

Open a **NEW** command prompt and run:

```cmd
tesseract --version
```

You should see version information. If you get "not recognized", PATH wasn't set correctly.

### Alternative: Manual Path Configuration

If you don't want to modify PATH, create a file `tesseract_config.py` in the bot directory:

```python
import pytesseract

# Point to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Then import this in the bot before running.

## Linux Installation

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Fedora/RHEL

```bash
sudo dnf install tesseract
```

### Verify

```bash
tesseract --version
```

## macOS Installation

### Using Homebrew

```bash
brew install tesseract
```

### Verify

```bash
tesseract --version
```

## Testing the Installation

After installing Tesseract, test it with the bot:

```bash
python check_dependencies.py
```

You should see:
```
✓ Tesseract OCR v5.x.x found
```

If you see an error, the installation didn't work correctly.

## Common Issues

### "pytesseract.pytesseract.TesseractNotFoundError"

**Cause:** Tesseract is installed but Python can't find it.

**Solution 1:** Add Tesseract to PATH (see Step 3 above)

**Solution 2:** Set the path in code:

Edit `vision_detector.py` and add after the imports:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### "tesseract is not recognized as an internal or external command"

**Cause:** Tesseract not in PATH

**Solution:**
1. Verify Tesseract is installed at `C:\Program Files\Tesseract-OCR`
2. Add to PATH (see Step 3)
3. Restart terminal

### "Permission denied"

**Cause:** Insufficient permissions

**Solution:**
- On Linux: Use `sudo` for installation
- On Windows: Run installer as Administrator

## Verification Script

Run this Python script to verify everything works:

```python
import pytesseract
from PIL import Image
import numpy as np

# Test Tesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract {version} is installed correctly!")

    # Create a simple test image with text
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGB', (200, 50), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "TEST 123", fill='black')

    # Try OCR
    text = pytesseract.image_to_string(img)
    print(f"✓ OCR test result: '{text.strip()}'")

    if "TEST" in text or "123" in text:
        print("✓ OCR is working correctly!")
    else:
        print("⚠ OCR working but accuracy may be low")

except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTesseract is not properly installed or configured.")
```

Save as `test_ocr.py` and run with `python test_ocr.py`

## Still Having Issues?

1. Completely uninstall Tesseract
2. Restart your computer
3. Reinstall Tesseract with default options
4. Add to PATH
5. Restart terminal
6. Run `python check_dependencies.py`

If still not working, open an issue on GitHub with:
- Your operating system
- Python version (`python --version`)
- Error messages
- Output of `tesseract --version` (if it works)
