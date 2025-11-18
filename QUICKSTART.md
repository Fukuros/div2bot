# Quick Start Guide

Get up and running with the Division 2 Elevator Bot in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- The Division 2 game installed
- Administrator/elevated privileges

## Installation Steps

### 1. Install Python Dependencies

Open terminal/command prompt in the bot directory and run:

```bash
pip install -r requirements.txt
```

### 2. Test Your Setup

#### Test Screen Capture

```bash
python test_capture.py
```

This will:
- Capture your screen
- Show the captured image
- Verify screen capture is working

Press any key to close the test windows.

#### Test Vision Detection

```bash
python test_detection.py
```

This will:
- Capture your screen
- Try to detect game UI elements
- Show detection results

**Note:** For best results, run this while The Division 2 is open!

### 3. Configure Key Bindings

Edit `config.yaml` and make sure your key bindings match your in-game controls:

```yaml
keybinds:
  forward: 'w'      # ← Change if you use different keys
  backward: 's'
  left: 'a'
  right: 'd'
  interact: 'f'     # ← Your interaction key
  sprint: 'shift'
```

### 4. Run the Bot

1. Start The Division 2
2. Navigate to Summit area
3. Position near an elevator
4. Run the bot:

```bash
python main.py
```

5. Watch it work! The bot will:
   - Search for elevator
   - Approach and enter
   - Wait for players
   - Exit if someone joins

6. Press `Ctrl+C` to stop

## First Time Tips

### Use Debug Mode

For your first run, use debug mode to see what's happening:

```bash
python main.py --debug
```

This opens a window showing:
- What the bot sees
- Current state
- Detection highlights

### Common Issues

**"Nothing detected"**
- Make sure you're near an elevator
- Check if the interaction prompt is visible
- Try lowering `template_threshold` in config.yaml

**"Input not working"**
- Run Python as administrator (Windows)
- Use sudo on Linux
- Check key bindings match your game

**"Bot exits immediately"**
- This is normal if no elevator is nearby
- Position closer to an elevator
- The bot will keep searching

### Customizing Wait Time

Edit `config.yaml`:

```yaml
movement:
  elevator_wait_time: 2.0  # ← Change this (in seconds)
```

Lower value = less waiting before going to summit
Higher value = more time for players to join

## What Next?

- Read the full [README.md](README.md) for detailed documentation
- Adjust detection sensitivity in config.yaml
- Report issues or contribute improvements

## Getting Help

If something isn't working:

1. Run with detailed logging:
   ```bash
   python main.py --log-level DEBUG --log-file bot.log
   ```

2. Check the log file: `bot.log`

3. Open an issue on GitHub with:
   - Your config file
   - Log output
   - Description of the problem
   - Your setup (resolution, window mode, etc.)

---

**Happy gaming! This tool is here to help you enjoy The Division 2.** 🎮
