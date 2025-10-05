# Pool Shot Predictor - Usage Guide

## Quick Start

### Installation
```bash
npm install
```

### Running the Application
```bash
npm start
```

## Step-by-Step Tutorial

### 1. Launch the App
Run `npm start` in your terminal. The overlay window will start hidden.

### 2. Show the Overlay
Press **Ctrl+Shift+P** (Windows/Linux) or **Cmd+Shift+P** (Mac) to show the overlay.

You'll see a control panel in the top-right corner of your screen.

### 3. Open a Pool Game
Open any pool game in any web browser:
- Online pool games (8 Ball Pool, Miniclip, etc.)
- Browser-based pool simulators
- Any webpage with a pool table

### 4. Setup Table Boundaries

1. Click the **"Setup Table Boundaries"** button in the control panel
2. Your screen will dim with overlay instructions
3. Click on the **top-left pocket** of the pool table in your browser
4. Click on the **bottom-right pocket** of the pool table
5. The overlay will calculate the 4 walls automatically

### 5. Configure Cue Ball Position

Enter the cue ball's X and Y screen coordinates in the control panel:
- **Cue Ball X**: Horizontal position (pixels from left edge of screen)
- **Cue Ball Y**: Vertical position (pixels from top edge of screen)

**Tip**: You can find coordinates by:
1. Taking a screenshot with coordinates shown
2. Using browser developer tools to inspect element positions
3. Estimating based on the table boundaries you just set

### 6. See Predictions

Move your mouse cursor over the pool table area. You'll see:
- **Solid green line**: Direct shot path (0 bounces)
- **Dashed yellow line**: 1-bounce bank shot
- **Dashed orange line**: 2-bounce bank shot
- **Additional colors**: 3-5 bounce shots (pink, purple, cyan)
- **Orange circles**: Bounce points on walls
- **Green dashed rectangle**: Table boundaries
- **White circle**: Cue ball position

### 7. Move the Control Panel

The control panel can be repositioned anywhere on screen:
- Click and hold the **green drag handle** (⋮⋮) at the top of the control panel
- Drag it to your preferred location
- Release to place it there

### 8. Adjust Settings

Use the sliders in the control panel:
- **Max Bounces**: Control how many bank shot predictions to show (0-5)
- **Prediction Length**: Control how far lines extend (1-5x table size)

### 9. Hide or Quit

- Click **"Hide Overlay"** or press **Ctrl+Shift+P** to hide the overlay
- Press **Ctrl+Shift+Q** to quit the application completely

## Global Hotkeys

These work even when the overlay is hidden:

| Hotkey | Windows/Linux | Mac | Action |
|--------|---------------|-----|--------|
| Toggle Overlay | Ctrl+Shift+P | Cmd+Shift+P | Show/hide overlay |
| Quit App | Ctrl+Shift+Q | Cmd+Shift+Q | Close application |

## Control Panel Features

### Drag Handle
- **Green header bar (⋮⋮)**: Click and drag to move the control panel anywhere on screen
- The panel stays within screen boundaries automatically

### Buttons
- **Setup Table Boundaries**: Enter setup mode to define table corners
- **Clear Boundaries**: Reset all boundaries and start over
- **Hide Overlay**: Temporarily hide the overlay window

### Inputs
- **Cue Ball X/Y**: Set the current position of the cue ball (in screen pixels)

### Sliders
- **Max Bounces**: Number of wall bounces to predict (0-5)
- **Prediction Length**: Distance multiplier for prediction lines (1-5x)

### Status Display
Shows current state and instructions at the bottom of the control panel.

## How the Overlay Works

### Transparent Window
The app creates a transparent, frameless window that covers your entire screen. It's always on top of other windows but doesn't block your view.

### Click-Through
During normal operation, mouse clicks pass through the overlay to the game below. Only the control panel captures clicks.

During setup mode, clicks are captured to define table boundaries.

### Real-Time Prediction
The overlay tracks your mouse position and calculates shot paths using:
1. Ray-casting for wall intersections
2. Reflection physics for bounces
3. Path tracing for multi-bounce shots

## Tips & Tricks

### Accurate Setup
- Make sure to click precisely on the pocket centers
- The bottom-right pocket must be below AND to the right of top-left
- If setup fails, click "Clear Boundaries" and try again

### Finding Cue Ball Position
- Pause the game if possible
- Use the table boundaries as reference
- The default position (25% from left, 50% from top) is often close

### Performance
- The overlay uses minimal CPU during prediction
- Reduce max bounces if you experience lag
- The overlay has no impact on game performance

### Multiple Monitors
- The overlay covers only the primary monitor
- Move your pool game to the primary monitor for best results

## Building Executables

Create standalone applications that don't require Node.js:

### Windows
```bash
npm run build:win
```
Creates an installer in `dist/` folder.

### macOS
```bash
npm run build:mac
```
Creates a .dmg file in `dist/` folder.

### Linux
```bash
npm run build:linux
```
Creates an AppImage in `dist/` folder.

### All Platforms
```bash
npm run build
```
Builds for all supported platforms.

## Troubleshooting

### Overlay doesn't show
- Press Ctrl+Shift+P to toggle
- Check if app is running (look in task manager)
- Restart the application

### Can't click the game
- Make sure you've exited setup mode
- Check that status shows "Table boundaries set"
- Click "Clear Boundaries" if stuck

### Predictions not visible
- Verify table boundaries are set correctly
- Check cue ball position is within boundaries
- Increase prediction length slider
- Ensure max bounces is > 0

### Setup mode stuck
- Click "Clear Boundaries"
- Press Ctrl+Shift+Q to quit and restart

### Wrong predictions
- Re-do table boundary setup more carefully
- Update cue ball position to current location
- Check that the pool table hasn't moved on screen

## Advanced Usage

### Custom Hotkeys
Edit `main.js` to change hotkey combinations:
```javascript
globalShortcut.register('CommandOrControl+Shift+P', () => {
    // Your custom hotkey action
});
```

### Custom Colors
Edit `overlay.js` to change prediction line colors:
```javascript
const colors = ['#00ff00', '#ffff00', '#ff8800', '#ff0088', '#8800ff', '#00ffff'];
```

### Adjust Line Thickness
Edit `overlay.js`:
```javascript
this.ctx.lineWidth = 3; // Change this value
```

## System Requirements

- **OS**: Windows 7+, macOS 10.11+, or modern Linux
- **RAM**: 100MB minimum
- **CPU**: Any modern processor
- **Display**: Any resolution (overlay adapts automatically)

## Privacy & Security

- The app only overlays graphics on your screen
- No data is collected or transmitted
- No internet connection required
- Source code is fully open and auditable

## Support

For issues or questions:
1. Check this usage guide
2. Review the README.md
3. Check the GitHub issues page
4. Create a new issue with detailed description

## License

MIT License - Free to use, modify, and distribute.
