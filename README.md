# Pool Shot Prediction Overlay

A **desktop application** that overlays shot prediction on ANY pool game webpage. Built with Electron for cross-platform compatibility.

## Overview

This is a transparent desktop overlay application that can be placed on top of ANY existing pool game running in a web browser. It provides real-time shot prediction and bounce visualization without modifying the underlying game.

## Key Features

- **Desktop Overlay App**: Runs as a standalone application that overlays on your screen
- **Works on ANY Webpage**: Can overlay on any pool game in any browser
- **2-Point Table Setup**: Define table boundaries by clicking just the top-left and bottom-right pockets
- **Automatic Wall Calculation**: The 4 walls are automatically calculated from the 2 pocket positions
- **Dynamic Prediction Lines**: Real-time shot prediction that updates as you move your mouse
- **Multi-Bounce Bank Shots**: Visualize shots with up to 5 wall bounces
- **Configurable Cue Ball**: Set cue ball position via coordinates
- **Global Hotkeys**: Control the overlay without switching windows

## Installation

### Prerequisites
- Node.js (v14 or higher)
- npm (comes with Node.js)

### Install Dependencies
```bash
npm install
```

## Usage

### Running the App
```bash
npm start
```

### Global Hotkeys
- **Ctrl+Shift+P** (Windows/Linux) or **Cmd+Shift+P** (Mac): Toggle overlay visibility
- **Ctrl+Shift+Q** (Windows/Linux) or **Cmd+Shift+Q** (Mac): Quit application

### Setup Instructions

1. **Launch the application** using `npm start`
2. **Press Ctrl+Shift+P** to show the overlay
3. **Open your pool game** in any web browser
4. **Click "Setup Table Boundaries"** in the control panel
5. **Click on the top-left pocket** of the pool table in the browser
6. **Click on the bottom-right pocket** of the pool table
7. The system will automatically:
   - Calculate the 4 walls from these 2 points
   - Set a default cue ball position
   - Enable the prediction overlay

8. **Set the cue ball position** by entering X and Y coordinates
9. **Move your mouse** over the pool table to see prediction lines

## How It Works

### Desktop Overlay Architecture
The app creates a transparent, always-on-top window that covers your entire screen. During normal operation, it's click-through (mouse events pass through to the game below). When you enter setup mode, it captures clicks to define table boundaries.

### Boundary Definition
Instead of requiring all 6 pocket positions, this overlay simplifies setup by using only 2 pockets:
- **Top-left pocket** (x1, y1)
- **Bottom-right pocket** (x2, y2)

From these, it calculates the 4 walls:
```javascript
walls = {
    left: x1,
    top: y1,
    right: x2,
    bottom: y2
}
```

### Prediction Lines
- **Solid lines**: Direct shots (0 bounces)
- **Dashed lines**: Bank shots (1+ bounces)
- **Color coding**: Different colors for each bounce level
  - Green: Direct (0 bounces)
  - Yellow: 1 bounce
  - Orange: 2 bounces
  - Pink: 3 bounces
  - Purple: 4 bounces
  - Cyan: 5 bounces
- **Orange circles**: Mark bounce points on walls

## Controls

- **Setup Table Boundaries**: Enter setup mode to define the 2 pockets
- **Clear Boundaries**: Reset the table boundaries
- **Hide Overlay**: Temporarily hide the overlay (or use Ctrl+Shift+P)
- **Cue Ball X/Y**: Set the cue ball position (in screen pixels)
- **Max Bounces**: Control how many wall bounces to predict (0-5)
- **Prediction Length**: Control how far prediction lines extend (1-5x table diagonal)

## Building Executables

Build standalone executables for distribution:

### Windows
```bash
npm run build:win
```

### macOS
```bash
npm run build:mac
```

### Linux
```bash
npm run build:linux
```

### All Platforms
```bash
npm run build
```

Built applications will be in the `dist/` folder.

## Files

### Main Application Files
- **main.js** - Electron main process (window management, hotkeys)
- **overlay.html** - Overlay UI with control panel
- **overlay.js** - Prediction system and rendering logic
- **preload.js** - Secure IPC bridge between renderer and main process
- **package.json** - Project configuration and dependencies

### Legacy Web Version (deprecated)
- **index.html** - Old web-based version
- **pool-overlay.js** - Old web overlay system
- **demo-game.html** - Demo pool game

## Technical Details

### Efficient Algorithms
- **Ray-casting**: O(1) wall intersection detection per wall
- **Path tracing**: Early termination on boundary exit
- **Canvas overlay**: Transparent rendering with minimal CPU usage
- **Click-through**: Mouse events pass through to underlying application except during setup

### Electron Features
- Transparent, frameless window
- Always-on-top overlay
- Global hotkeys for easy access
- Click-through capability
- Cross-platform compatibility

## Platform Compatibility

- **Windows**: 7, 8, 10, 11
- **macOS**: 10.11 (El Capitan) and later
- **Linux**: Most modern distributions

## Troubleshooting

### Overlay not showing
- Press Ctrl+Shift+P to toggle visibility
- Check if the app is running in the system tray

### Can't click through overlay
- Make sure you've completed setup mode
- Click "Clear Boundaries" and try again

### Predictions not visible
- Ensure table boundaries are set correctly
- Check that cue ball position is within the table bounds
- Adjust prediction length slider

## Development

### Project Structure
```
ball/
├── main.js           # Electron main process
├── overlay.html      # Renderer UI
├── overlay.js        # Overlay logic
├── preload.js        # IPC bridge
├── package.json      # Dependencies & build config
└── README.md         # Documentation
```

### Technology Stack
- **Electron**: Desktop application framework
- **HTML5 Canvas**: Rendering prediction lines
- **Pure JavaScript**: No external libraries for core logic

## License

MIT
