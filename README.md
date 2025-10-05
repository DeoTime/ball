# Pool Shot Prediction Overlay

A transparent overlay system that adds dynamic shot prediction and bounce visualization to any existing pool game.

## Overview

This project provides a prediction overlay that can be placed on top of any pool game running in an HTML container (iframe, embed, or canvas). Instead of creating a complete pool game, it focuses solely on adding prediction functionality to existing games.

## Key Features

- **Overlay Architecture**: Works on top of existing pool games without modifying them
- **2-Point Table Setup**: Define table boundaries by clicking just the top-left and bottom-right pockets
- **Automatic Wall Calculation**: The 4 walls are automatically calculated from the 2 pocket positions
- **Dynamic Prediction Lines**: Real-time shot prediction that updates as you move your mouse
- **Multi-Bounce Bank Shots**: Visualize shots with up to 5 wall bounces
- **Configurable Cue Ball**: Set cue ball position via coordinates
- **Toggle On/Off**: Enable or disable the overlay at any time

## Setup Instructions

1. **Open index.html** in a web browser
2. **Click "Setup Table Boundaries"**
3. **Click on the top-left pocket** of your pool table
4. **Click on the bottom-right pocket** of your pool table
5. The system will automatically:
   - Calculate the 4 walls from these 2 points
   - Set a default cue ball position
   - Enable the prediction overlay

6. **Set the cue ball position** by entering X and Y coordinates
7. **Move your mouse** over the table to see prediction lines

## How It Works

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

### Integration with Existing Games

The overlay uses a transparent canvas positioned absolutely over the game container. It doesn't interfere with the underlying game - it only adds visual prediction lines on top.

```html
<div class="game-container">
    <iframe src="your-pool-game.html"></iframe>
    <canvas id="overlayCanvas"></canvas> <!-- Transparent overlay -->
</div>
```

## Controls

- **Setup Table Boundaries**: Enter setup mode to define the 2 pockets
- **Clear Boundaries**: Reset the table boundaries
- **Toggle Overlay**: Turn predictions on/off
- **Cue Ball X/Y**: Set the cue ball position (in pixels)
- **Max Bounces**: Control how many wall bounces to predict (0-5)
- **Prediction Length**: Control how far prediction lines extend (1-5x table diagonal)

## Files

- **index.html** - Main UI with overlay controls
- **pool-overlay.js** - Overlay prediction system
- **demo-game.html** - Demo pool game for testing (replace with your own game)

## Technical Details

### Efficient Algorithms
- **Ray-casting**: O(1) wall intersection per wall
- **Path tracing**: Early termination on boundary exit
- **Canvas overlay**: Zero impact on underlying game performance

### Customization

You can customize the overlay by modifying `pool-overlay.js`:
- Change prediction line colors
- Adjust line thickness and dash patterns
- Modify bounce indicator appearance
- Add additional features like pocket targeting

## Browser Compatibility

Works in all modern browsers with HTML5 Canvas support:
- Chrome/Edge
- Firefox
- Safari
- Opera

## Integration Guide

To integrate with your own pool game:

1. Replace `demo-game.html` with your game's URL in `index.html`
2. Ensure your game is in an iframe or container
3. Use the overlay controls to set up table boundaries
4. The overlay will draw predictions on top of your game
