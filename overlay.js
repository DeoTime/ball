// Desktop Overlay Prediction System for Electron
class DesktopPoolOverlay {
    constructor() {
        this.canvas = document.getElementById('overlayCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.setupOverlay = document.getElementById('setupOverlay');
        this.setupMessage = document.getElementById('setupMessage');
        
        // Setup state
        this.setupMode = false;
        this.clickCount = 0;
        this.topLeftPocket = null;
        this.bottomRightPocket = null;
        this.walls = null;
        
        // Cue ball position
        this.cueBall = { x: null, y: null };
        this.mousePos = { x: 0, y: 0 };
        
        // Settings
        this.maxBounces = 2;
        this.predictionLengthMultiplier = 3.0;
        this.overlayEnabled = false;
        
        // Drag state for control panel
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        // Resize canvas to screen
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Setup event listeners
        this.setupEventListeners();
        this.setupDragListeners();
        
        // Start animation
        this.animate();
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    setupEventListeners() {
        // Setup button
        document.getElementById('setupBtn').addEventListener('click', () => {
            this.startSetup();
        });
        
        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearBoundaries();
        });
        
        // Minimize button
        document.getElementById('minimizeBtn').addEventListener('click', () => {
            if (window.electronAPI) {
                window.electronAPI.minimizeApp();
            }
        });
        
        // Canvas click for setup
        document.addEventListener('click', (e) => {
            if (this.setupMode && !this.isDragging) {
                this.handleSetupClick(e);
            }
        });
        
        // Mouse move for prediction
        document.addEventListener('mousemove', (e) => {
            this.mousePos = { x: e.clientX, y: e.clientY };
        });
        
        // Cue ball position inputs
        document.getElementById('cueBallX').addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (!isNaN(val)) {
                this.cueBall.x = val;
                document.getElementById('cueBallXValue').textContent = val.toFixed(0);
            }
        });
        
        document.getElementById('cueBallY').addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (!isNaN(val)) {
                this.cueBall.y = val;
                document.getElementById('cueBallYValue').textContent = val.toFixed(0);
            }
        });
        
        // Max bounces slider
        document.getElementById('maxBounces').addEventListener('input', (e) => {
            this.maxBounces = parseInt(e.target.value);
            document.getElementById('maxBouncesValue').textContent = this.maxBounces;
        });
        
        // Prediction length slider
        document.getElementById('predictionLength').addEventListener('input', (e) => {
            this.predictionLengthMultiplier = parseFloat(e.target.value);
            document.getElementById('predictionLengthValue').textContent = this.predictionLengthMultiplier.toFixed(1) + 'x';
        });
    }
    
    setupDragListeners() {
        const dragHandle = document.getElementById('dragHandle');
        const controlPanel = document.getElementById('controlPanel');
        
        dragHandle.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            const rect = controlPanel.getBoundingClientRect();
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const newX = e.clientX - this.dragOffset.x;
                const newY = e.clientY - this.dragOffset.y;
                
                // Keep panel within screen bounds
                const maxX = window.innerWidth - controlPanel.offsetWidth;
                const maxY = window.innerHeight - controlPanel.offsetHeight;
                
                const clampedX = Math.max(0, Math.min(newX, maxX));
                const clampedY = Math.max(0, Math.min(newY, maxY));
                
                controlPanel.style.left = clampedX + 'px';
                controlPanel.style.top = clampedY + 'px';
                controlPanel.style.right = 'auto';
                
                e.preventDefault();
            }
        });
        
        document.addEventListener('mouseup', () => {
            this.isDragging = false;
        });
    }
    
    startSetup() {
        this.setupMode = true;
        this.clickCount = 0;
        this.topLeftPocket = null;
        this.bottomRightPocket = null;
        this.walls = null;
        this.overlayEnabled = false;
        
        // Show setup overlay
        this.setupOverlay.classList.add('active');
        this.setupMessage.textContent = 'Click on the TOP-LEFT pocket';
        
        const statusEl = document.getElementById('status');
        statusEl.textContent = 'Click on the TOP-LEFT pocket (step 1 of 2)';
        statusEl.classList.add('setup');
        
        const setupBtn = document.getElementById('setupBtn');
        setupBtn.textContent = 'Setting up... (1/2)';
        setupBtn.disabled = true;
        
        // Notify Electron to enable mouse events
        if (window.electronAPI) {
            window.electronAPI.setSetupMode(true);
        }
    }
    
    handleSetupClick(e) {
        this.clickCount++;
        
        if (this.clickCount === 1) {
            // First click - top-left pocket
            this.topLeftPocket = { x: e.clientX, y: e.clientY };
            
            this.setupMessage.textContent = 'Now click on the BOTTOM-RIGHT pocket';
            
            const statusEl = document.getElementById('status');
            statusEl.textContent = `Top-left set at (${e.clientX.toFixed(0)}, ${e.clientY.toFixed(0)}). Now click BOTTOM-RIGHT pocket (step 2 of 2)`;
            
            document.getElementById('setupBtn').textContent = 'Setting up... (2/2)';
        } else if (this.clickCount === 2) {
            // Second click - bottom-right pocket
            this.bottomRightPocket = { x: e.clientX, y: e.clientY };
            this.finishSetup();
        }
    }
    
    finishSetup() {
        // Calculate the 4 walls from the 2 pockets
        this.walls = {
            left: this.topLeftPocket.x,
            top: this.topLeftPocket.y,
            right: this.bottomRightPocket.x,
            bottom: this.bottomRightPocket.y
        };
        
        // Validate
        if (this.walls.right <= this.walls.left || this.walls.bottom <= this.walls.top) {
            alert('Invalid pocket positions. Bottom-right must be below and to the right of top-left. Please try again.');
            this.clearBoundaries();
            return;
        }
        
        // Setup complete
        this.setupMode = false;
        this.setupOverlay.classList.remove('active');
        
        const statusEl = document.getElementById('status');
        statusEl.textContent = `Table boundaries set. Top-left: (${this.topLeftPocket.x.toFixed(0)}, ${this.topLeftPocket.y.toFixed(0)}), Bottom-right: (${this.bottomRightPocket.x.toFixed(0)}, ${this.bottomRightPocket.y.toFixed(0)})`;
        statusEl.classList.remove('setup');
        
        document.getElementById('setupBtn').textContent = 'Setup Table Boundaries';
        document.getElementById('setupBtn').disabled = false;
        
        // Auto-enable overlay
        this.overlayEnabled = true;
        
        // Set default cue ball position (center-left of table)
        const defaultX = this.walls.left + (this.walls.right - this.walls.left) * 0.25;
        const defaultY = this.walls.top + (this.walls.bottom - this.walls.top) * 0.5;
        this.cueBall = { x: defaultX, y: defaultY };
        
        document.getElementById('cueBallX').value = defaultX.toFixed(0);
        document.getElementById('cueBallY').value = defaultY.toFixed(0);
        document.getElementById('cueBallXValue').textContent = defaultX.toFixed(0);
        document.getElementById('cueBallYValue').textContent = defaultY.toFixed(0);
        
        // Notify Electron to disable mouse events (click-through)
        if (window.electronAPI) {
            window.electronAPI.setSetupMode(false);
        }
    }
    
    clearBoundaries() {
        this.setupMode = false;
        this.clickCount = 0;
        this.topLeftPocket = null;
        this.bottomRightPocket = null;
        this.walls = null;
        this.overlayEnabled = false;
        
        this.setupOverlay.classList.remove('active');
        
        const statusEl = document.getElementById('status');
        statusEl.textContent = 'Boundaries cleared. Press "Setup Table Boundaries" to begin.';
        statusEl.classList.remove('setup');
        
        document.getElementById('setupBtn').textContent = 'Setup Table Boundaries';
        document.getElementById('setupBtn').disabled = false;
        
        // Notify Electron
        if (window.electronAPI) {
            window.electronAPI.setSetupMode(false);
        }
    }
    
    calculateDirection(from, to) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const length = Math.sqrt(dx * dx + dy * dy);
        return { dx: dx / length, dy: dy / length, length };
    }
    
    reflectDirection(dir, wall) {
        if (wall === 'horizontal') {
            return { dx: dir.dx, dy: -dir.dy };
        } else if (wall === 'vertical') {
            return { dx: -dir.dx, dy: dir.dy };
        }
        return dir;
    }
    
    findWallIntersection(pos, dir, maxDistance) {
        const intersections = [];
        
        // Top wall
        if (dir.dy < 0) {
            const t = (this.walls.top - pos.y) / dir.dy;
            if (t > 0 && t < maxDistance) {
                const x = pos.x + dir.dx * t;
                if (x >= this.walls.left && x <= this.walls.right) {
                    intersections.push({ x, y: this.walls.top, distance: t, wall: 'horizontal' });
                }
            }
        }
        
        // Bottom wall
        if (dir.dy > 0) {
            const t = (this.walls.bottom - pos.y) / dir.dy;
            if (t > 0 && t < maxDistance) {
                const x = pos.x + dir.dx * t;
                if (x >= this.walls.left && x <= this.walls.right) {
                    intersections.push({ x, y: this.walls.bottom, distance: t, wall: 'horizontal' });
                }
            }
        }
        
        // Left wall
        if (dir.dx < 0) {
            const t = (this.walls.left - pos.x) / dir.dx;
            if (t > 0 && t < maxDistance) {
                const y = pos.y + dir.dy * t;
                if (y >= this.walls.top && y <= this.walls.bottom) {
                    intersections.push({ x: this.walls.left, y, distance: t, wall: 'vertical' });
                }
            }
        }
        
        // Right wall
        if (dir.dx > 0) {
            const t = (this.walls.right - pos.x) / dir.dx;
            if (t > 0 && t < maxDistance) {
                const y = pos.y + dir.dy * t;
                if (y >= this.walls.top && y <= this.walls.bottom) {
                    intersections.push({ x: this.walls.right, y, distance: t, wall: 'vertical' });
                }
            }
        }
        
        if (intersections.length > 0) {
            return intersections.reduce((closest, curr) => 
                curr.distance < closest.distance ? curr : closest
            );
        }
        return null;
    }
    
    tracePath(startPos, direction, maxDistance, bounces = 0) {
        const path = [{ x: startPos.x, y: startPos.y }];
        let currentPos = { ...startPos };
        let currentDir = { ...direction };
        let remainingDistance = maxDistance;
        let currentBounces = 0;
        
        while (remainingDistance > 0 && currentBounces <= bounces) {
            const wallHit = this.findWallIntersection(currentPos, currentDir, remainingDistance);
            
            if (wallHit) {
                path.push({ x: wallHit.x, y: wallHit.y, bounce: true });
                currentPos = { x: wallHit.x, y: wallHit.y };
                currentDir = this.reflectDirection(currentDir, wallHit.wall);
                remainingDistance -= wallHit.distance;
                currentBounces++;
            } else {
                const endX = currentPos.x + currentDir.dx * remainingDistance;
                const endY = currentPos.y + currentDir.dy * remainingDistance;
                path.push({ x: endX, y: endY });
                break;
            }
        }
        
        return path;
    }
    
    drawPredictionLine(path, isDashed = false, color = '#00ff00') {
        if (path.length < 2) return;
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3;
        this.ctx.globalAlpha = isDashed ? 0.6 : 0.8;
        
        if (isDashed) {
            this.ctx.setLineDash([10, 5]);
        } else {
            this.ctx.setLineDash([]);
        }
        
        this.ctx.beginPath();
        this.ctx.moveTo(path[0].x, path[0].y);
        
        for (let i = 1; i < path.length; i++) {
            this.ctx.lineTo(path[i].x, path[i].y);
            
            if (path[i].bounce) {
                this.ctx.stroke();
                // Draw bounce indicator
                this.ctx.fillStyle = '#ffaa00';
                this.ctx.beginPath();
                this.ctx.arc(path[i].x, path[i].y, 6, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.moveTo(path[i].x, path[i].y);
            }
        }
        
        this.ctx.stroke();
        this.ctx.globalAlpha = 1.0;
        this.ctx.setLineDash([]);
    }
    
    drawPredictions() {
        if (!this.overlayEnabled || !this.walls || this.cueBall.x === null || this.cueBall.y === null) {
            return;
        }
        
        const aimDir = this.calculateDirection(this.cueBall, this.mousePos);
        
        if (aimDir.length < 10) return;
        
        const tableWidth = this.walls.right - this.walls.left;
        const tableHeight = this.walls.bottom - this.walls.top;
        const tableDiagonal = Math.sqrt(tableWidth * tableWidth + tableHeight * tableHeight);
        const maxPredictionDistance = tableDiagonal * this.predictionLengthMultiplier;
        
        for (let b = 0; b <= this.maxBounces; b++) {
            const path = this.tracePath(this.cueBall, aimDir, maxPredictionDistance, b);
            const isDashed = b > 0;
            const colors = ['#00ff00', '#ffff00', '#ff8800', '#ff0088', '#8800ff', '#00ffff'];
            const color = colors[b % colors.length];
            this.drawPredictionLine(path, isDashed, color);
        }
    }
    
    drawBoundaryVisualization() {
        if (!this.walls) return;
        
        // Draw boundary rectangle
        this.ctx.strokeStyle = '#00ff00';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(
            this.walls.left,
            this.walls.top,
            this.walls.right - this.walls.left,
            this.walls.bottom - this.walls.top
        );
        this.ctx.setLineDash([]);
        
        // Draw pocket markers
        this.ctx.fillStyle = '#00ff00';
        this.ctx.beginPath();
        this.ctx.arc(this.topLeftPocket.x, this.topLeftPocket.y, 8, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(this.bottomRightPocket.x, this.bottomRightPocket.y, 8, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw cue ball position if set
        if (this.cueBall.x !== null && this.cueBall.y !== null) {
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.cueBall.x, this.cueBall.y, 15, 0, Math.PI * 2);
            this.ctx.stroke();
            
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            this.ctx.fill();
        }
    }
    
    drawSetupGuide() {
        if (!this.setupMode || !this.topLeftPocket) return;
        
        // Draw first pocket marker
        this.ctx.fillStyle = '#00ff00';
        this.ctx.shadowColor = '#00ff00';
        this.ctx.shadowBlur = 20;
        this.ctx.beginPath();
        this.ctx.arc(this.topLeftPocket.x, this.topLeftPocket.y, 12, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.shadowBlur = 0;
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.setupMode) {
            this.drawSetupGuide();
        } else {
            this.drawPredictions();
            this.drawBoundaryVisualization();
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize the overlay system
window.addEventListener('DOMContentLoaded', () => {
    new DesktopPoolOverlay();
});
