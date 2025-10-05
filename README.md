# Pool Shot Predictor

An interactive pool/billiards shot prediction engine that visualizes direct shots and bank shots (bounce shots) in real-time as you aim.

## Features

- **Dynamic Shot Prediction**: Real-time prediction lines that update as you move your mouse to aim
- **Direct Shot Visualization**: Solid green line shows the direct path from cue ball to target
- **Bank Shot Prediction**: Dashed colored lines show possible bounce shots off table walls
- **Multi-Bounce Support**: Configurable prediction for up to 5 bounces with color-coded paths
- **Ball Collision Detection**: Highlights when prediction line intersects with target balls
- **Interactive Controls**: Adjust max bounces and prediction length in real-time
- **Visual Feedback**: Bounce points marked with orange indicators

## Usage

1. Open `index.html` in a web browser
2. Move your mouse over the pool table to aim the cue
3. Prediction lines will update in real-time showing possible shot paths:
   - **Solid green line**: Direct shot (0 bounces)
   - **Dashed yellow line**: 1-bounce bank shot
   - **Dashed orange line**: 2-bounce bank shot
   - **Additional colors**: 3+ bounce shots
4. Use the controls to adjust:
   - **Max Bounces**: How many wall bounces to predict (0-5)
   - **Prediction Length**: How far to extend prediction lines
5. Click **Reset Balls** to return balls to starting positions

## Implementation Details

### Architecture
- Pure HTML5/Canvas implementation with no external dependencies
- Efficient ray-casting algorithm for wall collision detection
- Real-time physics simulation for bounce angle calculations
- Optimized rendering using requestAnimationFrame

### Table Boundaries
The four bounding walls are configurable through the `walls` object in `pool-engine.js`:
```javascript
this.walls = {
    top: this.wallThickness,
    bottom: this.height - this.wallThickness,
    left: this.wallThickness,
    right: this.width - this.wallThickness
};
```

### Bounce Physics
Bank shots use accurate reflection physics:
- Horizontal walls: reflect Y-direction velocity
- Vertical walls: reflect X-direction velocity
- Maintains realistic shot predictions

## Screenshots

![Pool Shot Predictor](https://github.com/user-attachments/assets/fc4b1075-10a6-4d56-aa90-c86bac255ee8)
*Initial view with prediction lines showing direct and bank shot paths*

![Aiming at target ball](https://github.com/user-attachments/assets/09c4b6b4-404b-4416-8c41-4343e34925b7)
*Real-time prediction updates as you aim, showing ball collision detection*

![Multi-bounce predictions](https://github.com/user-attachments/assets/1d4f4667-f8bf-48d8-84cf-35f6b44de7bc)
*Multiple bounce predictions with color-coded paths (up to 4 bounces shown)*

## Files

- `index.html` - Main HTML page with UI and styling
- `pool-engine.js` - Core pool engine with prediction algorithms

## Browser Compatibility

Works in all modern browsers that support HTML5 Canvas:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera
