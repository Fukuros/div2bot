# Division 2 Elevator Bot

An accessibility automation tool for The Division 2 that helps with elevator navigation. Designed specifically for disabled players who need assistance with repetitive game actions.

## 🎯 Purpose

This bot automates elevator usage in The Division 2 Summit mode:
- Detects and approaches elevators
- Enters elevators automatically
- Waits in elevator for other players
- Exits when another player joins (using `/leave` command)
- Works at any resolution (windowed or borderless fullscreen)

**Important:** This tool is designed for accessibility purposes to assist disabled players.

## ✨ Features

- **Active Search Pattern**: Automatically rotates camera and looks around for elevators
- **Resolution Independent**: Works at any screen resolution
- **Window Mode Flexible**: Supports windowed and borderless modes
- **Computer Vision Based**: Uses only screen capture (no memory reading or game hooks)
- **Chat Command Integration**: Uses `/leave` command to exit when players join
- **State Machine**: Intelligent state management for robust operation
- **Configurable**: Extensive configuration options via YAML
- **Debug Mode**: Visual feedback for troubleshooting

## 🔧 Requirements

- Python 3.8 or higher
- Windows 10/11 (primary support) or Linux (experimental)
- The Division 2 installed and running
- Administrator/elevated privileges (for input simulation)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Fukuros/div2bot.git
cd div2bot
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python main.py --help
```

## 🚀 Usage

### Basic Usage

1. Start The Division 2 and navigate to the Summit area
2. Position your character near an elevator
3. Run the bot:

```bash
python main.py
```

4. The bot will automatically:
   - **Actively search** for elevators (rotates camera, looks around)
   - Approach and enter when found
   - Wait for other players
   - Exit if someone joins (using `/leave` command)

5. Press `Ctrl+C` to stop the bot

**Note:** The bot uses an active search pattern - it will rotate the camera and move around looking for elevator interaction prompts. For best results, start the bot in the general vicinity of an elevator.

### Advanced Usage

#### Debug Mode

See what the bot is detecting in real-time:

```bash
python main.py --debug
```

This opens a window showing:
- Current state
- Detection overlays
- Time in state

#### Custom Configuration

Create your own config file:

```bash
python main.py --config my_config.yaml
```

#### Logging

Save logs to a file:

```bash
python main.py --log-file bot.log --log-level DEBUG
```

## ⚙️ Configuration

Edit `config.yaml` to customize bot behavior:

### Key Bindings

Match your in-game controls:

```yaml
keybinds:
  forward: 'w'
  backward: 's'
  left: 'a'
  right: 'd'
  interact: 'f'
  sprint: 'shift'
  chat: 'enter'  # Key to open chat (for /leave command)
```

### Detection Settings

Adjust sensitivity:

```yaml
detection:
  template_threshold: 0.7  # Higher = more strict (0.0 to 1.0)
  capture_interval: 0.1    # How often to check screen (seconds)
```

### Movement Timing

Fine-tune movement:

```yaml
movement:
  move_duration: 0.5          # How long to hold movement keys
  interact_duration: 0.2      # How long to hold interact key
  elevator_wait_time: 2.0     # How long to wait in elevator
```

## 🏗️ Architecture

The bot consists of several modular components:

### Core Modules

- **screen_capture.py**: Resolution-independent screen capture
- **vision_detector.py**: Computer vision for game element detection
- **state_machine.py**: State management and transitions
- **input_controller.py**: Keyboard/mouse input simulation
- **elevator_bot.py**: Main bot logic and coordination
- **main.py**: Entry point and CLI interface

### State Flow

```
IDLE
  ↓
SEARCHING_ELEVATOR → Actively rotate camera and look for elevator prompt
  ↓                  (360° rotation every 4 steps, incremental search otherwise)
APPROACHING_ELEVATOR → Move towards elevator
  ↓
ENTERING_ELEVATOR → Press interact key
  ↓
IN_ELEVATOR → Confirm entry
  ↓
WAITING_IN_ELEVATOR → Monitor for players
  ↓
PLAYER_DETECTED → Someone joined, execute /leave command
  ↓
EXITING_ELEVATOR → Move out and leave group
  ↓
(back to SEARCHING_ELEVATOR)
```

## 🔍 How It Works

### Vision Detection

The bot uses computer vision techniques to identify game elements:

1. **Color Detection**: Identifies UI elements by their characteristic colors
   - Orange/yellow for interaction prompts
   - White/blue for player tags
   - Gray/white for floor indicators

2. **Template Matching**: Can match saved template images for precise detection

3. **Movement Detection**: Compares frames to detect scene changes

### Chat Command Integration

When another player joins the elevator, the bot:
1. Opens the chat window (Enter key)
2. Types `/leave` command
3. Sends the command (Enter key)
4. Exits the elevator automatically

This ensures clean exit without disrupting other players' gameplay.

### Active Search Pattern

The bot doesn't just wait passively - it actively searches for elevators:

1. **Camera Rotation**: Every 2 seconds, rotates the camera to scan for interaction prompts
2. **360° Scanning**: Every 4th search step, performs a full 360-degree rotation
3. **Incremental Movement**: Between full rotations, makes small movements while rotating
4. **Continuous Detection**: Constantly analyzes screen for orange/yellow elevator prompts

This means you can start the bot in the general area and it will find the elevator, rather than needing to be perfectly positioned.

**Search Behavior:**
- Step 1-3: Rotate 90° + small forward movement
- Step 4: Full 360° rotation (8 segments)
- Repeat

### No Game Hooks

This bot does NOT:
- Read game memory
- Inject code into the game
- Hook DirectX/rendering
- Modify game files

It only:
- Captures screen images
- Analyzes captured images
- Simulates keyboard input

## 🐛 Troubleshooting

### Bot doesn't detect elevator

1. Ensure you're close enough to see the interaction prompt
2. Try adjusting `template_threshold` in config (lower = more lenient)
3. Run in `--debug` mode to see what's being detected
4. Check lighting conditions in-game (avoid very dark areas)

### Input not working

1. Run Python with administrator/elevated privileges
2. Verify key bindings match your in-game settings
3. Make sure The Division 2 window is focused

### Bot gets stuck in a state

1. Check the timeout setting in config: `max_state_time`
2. The bot will auto-recover after timeout
3. Use `Ctrl+C` to safely stop and restart

### Resolution issues

1. The bot auto-detects your resolution
2. Make sure The Division 2 is running before starting the bot
3. For multi-monitor setups, the bot uses your primary monitor

## 🛠️ Development

### Adding New States

1. Add state to `BotState` enum in `state_machine.py`
2. Create handler method in `elevator_bot.py`: `handle_your_state()`
3. Add state to main update loop
4. Update state descriptions

### Improving Detection

1. Capture screenshots of UI elements you want to detect
2. Analyze their colors/features using OpenCV
3. Add detection method to `vision_detector.py`
4. Test with various lighting conditions and resolutions

### Testing

Create test scripts in the repository:

```python
from screen_capture import ScreenCapture
from vision_detector import VisionDetector

# Test screen capture
screen = ScreenCapture()
img = screen.capture()
print(f"Captured {img.shape}")

# Test vision detection
vision = VisionDetector()
result = vision.detect_ui_element_by_color(img, 'elevator_prompt')
print(f"Detected: {result.detected}, Confidence: {result.confidence}")
```

## 📝 License

This project is provided as-is for accessibility purposes. Use responsibly and in accordance with game terms of service.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## ⚠️ Disclaimer

This tool is designed specifically for accessibility purposes to help disabled players enjoy The Division 2.

**Please note:**
- This is an automation tool that simulates input
- Use at your own discretion and risk
- The authors are not responsible for any consequences of using this tool
- Always follow game terms of service and community guidelines

## 🙏 Acknowledgments

Created to help disabled gamers enjoy The Division 2 with reduced physical strain.

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Provide logs with `--log-level DEBUG`
- Include your config file (remove sensitive info)
- Describe your setup (resolution, window mode, etc.)

---

**Made with ❤️ for accessibility in gaming**
