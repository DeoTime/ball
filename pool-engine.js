// Pool Engine - Shot Prediction and Bounce Visualization

class PoolEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        
        // Table boundaries (walls)
        this.wallThickness = 30;
        this.walls = {
            top: this.wallThickness,
            bottom: this.height - this.wallThickness,
            left: this.wallThickness,
            right: this.width - this.wallThickness
        };
        
        // Pockets (6 standard pool table pockets)
        this.pocketRadius = 20;
        this.pockets = [
            { x: this.walls.left, y: this.walls.top, label: 'Top-Left' },
            { x: this.width / 2, y: this.walls.top, label: 'Top-Middle' },
            { x: this.walls.right, y: this.walls.top, label: 'Top-Right' },
            { x: this.walls.left, y: this.walls.bottom, label: 'Bottom-Left' },
            { x: this.width / 2, y: this.walls.bottom, label: 'Bottom-Middle' },
            { x: this.walls.right, y: this.walls.bottom, label: 'Bottom-Right' }
        ];
        
        // Balls
        this.ballRadius = 12;
        this.cueBall = { x: this.width / 4, y: this.height / 2, color: '#fff' };
        this.targetBalls = [
            { x: this.width * 0.6, y: this.height * 0.3, color: '#ff0000' },
            { x: this.width * 0.65, y: this.height * 0.5, color: '#ffff00' },
            { x: this.width * 0.7, y: this.height * 0.7, color: '#0000ff' }
        ];
        
        // Aiming
        this.mousePos = { x: 0, y: 0 };
        this.maxBounces = 2;
        this.predictionLengthMultiplier = 3.0;
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start animation loop
        this.animate();
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mousePos = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        });
        
        document.getElementById('maxBounces').addEventListener('input', (e) => {
            this.maxBounces = parseInt(e.target.value);
            document.getElementById('maxBouncesValue').textContent = this.maxBounces;
        });
        
        document.getElementById('predictionLength').addEventListener('input', (e) => {
            this.predictionLengthMultiplier = parseFloat(e.target.value);
            document.getElementById('predictionLengthValue').textContent = this.predictionLengthMultiplier.toFixed(1) + 'x';
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetBalls();
        });
    }
    
    resetBalls() {
        this.cueBall = { x: this.width / 4, y: this.height / 2, color: '#fff' };
        this.targetBalls = [
            { x: this.width * 0.6, y: this.height * 0.3, color: '#ff0000' },
            { x: this.width * 0.65, y: this.height * 0.5, color: '#ffff00' },
            { x: this.width * 0.7, y: this.height * 0.7, color: '#0000ff' }
        ];
    }
    
    drawTable() {
        // Draw playing surface
        this.ctx.fillStyle = '#0d5d0d';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw walls
        this.ctx.fillStyle = '#8b4513';
        this.ctx.fillRect(0, 0, this.width, this.walls.top); // Top wall
        this.ctx.fillRect(0, this.walls.bottom, this.width, this.wallThickness); // Bottom wall
        this.ctx.fillRect(0, 0, this.walls.left, this.height); // Left wall
        this.ctx.fillRect(this.walls.right, 0, this.wallThickness, this.height); // Right wall
        
        // Draw wall borders
        this.ctx.strokeStyle = '#654321';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(this.walls.left, this.walls.top, 
            this.walls.right - this.walls.left, 
            this.walls.bottom - this.walls.top);
    }
    
    drawPockets() {
        this.pockets.forEach(pocket => {
            this.ctx.fillStyle = '#000';
            this.ctx.beginPath();
            this.ctx.arc(pocket.x, pocket.y, this.pocketRadius, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Pocket highlight
            this.ctx.strokeStyle = '#333';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        });
    }
    
    drawBall(ball) {
        // Ball shadow
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.beginPath();
        this.ctx.arc(ball.x + 2, ball.y + 2, this.ballRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Ball
        this.ctx.fillStyle = ball.color;
        this.ctx.beginPath();
        this.ctx.arc(ball.x, ball.y, this.ballRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Ball highlight
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.beginPath();
        this.ctx.arc(ball.x - 4, ball.y - 4, 4, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Ball outline
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(ball.x, ball.y, this.ballRadius, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    calculateDirection(from, to) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const length = Math.sqrt(dx * dx + dy * dy);
        return { dx: dx / length, dy: dy / length, length };
    }
    
    reflectDirection(dir, wall) {
        // Reflect direction vector based on wall
        if (wall === 'horizontal') {
            return { dx: dir.dx, dy: -dir.dy };
        } else if (wall === 'vertical') {
            return { dx: -dir.dx, dy: dir.dy };
        }
        return dir;
    }
    
    findWallIntersection(pos, dir, maxDistance) {
        // Calculate intersections with all walls
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
        
        // Return closest intersection
        if (intersections.length > 0) {
            return intersections.reduce((closest, curr) => 
                curr.distance < closest.distance ? curr : closest
            );
        }
        return null;
    }
    
    findBallIntersection(pos, dir, maxDistance, excludeBall = null) {
        let closestIntersection = null;
        let closestDistance = maxDistance;
        
        const ballsToCheck = this.targetBalls.filter(ball => ball !== excludeBall);
        
        for (const ball of ballsToCheck) {
            // Check if ray intersects with ball
            const toBall = { x: ball.x - pos.x, y: ball.y - pos.y };
            const projection = toBall.x * dir.dx + toBall.y * dir.dy;
            
            if (projection > 0) {
                const closestPoint = {
                    x: pos.x + dir.dx * projection,
                    y: pos.y + dir.dy * projection
                };
                
                const distToBall = Math.sqrt(
                    Math.pow(closestPoint.x - ball.x, 2) + 
                    Math.pow(closestPoint.y - ball.y, 2)
                );
                
                const combinedRadius = this.ballRadius * 2;
                if (distToBall < combinedRadius && projection < closestDistance) {
                    closestDistance = projection;
                    closestIntersection = { ball, distance: projection };
                }
            }
        }
        
        return closestIntersection;
    }
    
    tracePath(startPos, direction, maxDistance, bounces = 0) {
        const path = [{ x: startPos.x, y: startPos.y }];
        let currentPos = { ...startPos };
        let currentDir = { ...direction };
        let remainingDistance = maxDistance;
        let currentBounces = 0;
        
        while (remainingDistance > 0 && currentBounces <= bounces) {
            // Check for ball collision first
            const ballHit = this.findBallIntersection(currentPos, currentDir, remainingDistance);
            
            // Check for wall collision
            const wallHit = this.findWallIntersection(currentPos, currentDir, remainingDistance);
            
            // Determine what we hit first
            if (ballHit && (!wallHit || ballHit.distance < wallHit.distance)) {
                // Hit a ball
                const endX = currentPos.x + currentDir.dx * ballHit.distance;
                const endY = currentPos.y + currentDir.dy * ballHit.distance;
                path.push({ x: endX, y: endY, hitBall: ballHit.ball });
                break; // Stop at ball collision
            } else if (wallHit) {
                // Hit a wall
                path.push({ x: wallHit.x, y: wallHit.y, bounce: true });
                currentPos = { x: wallHit.x, y: wallHit.y };
                currentDir = this.reflectDirection(currentDir, wallHit.wall);
                remainingDistance -= wallHit.distance;
                currentBounces++;
            } else {
                // No collision, draw to max distance
                const endX = currentPos.x + currentDir.dx * remainingDistance;
                const endY = currentPos.y + currentDir.dy * remainingDistance;
                path.push({ x: endX, y: endY });
                break;
            }
        }
        
        return path;
    }
    
    drawPredictionLine(path, isDashed = false, color = '#00ff00', bounceNumber = 0) {
        if (path.length < 2) return;
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 2;
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
            
            // Draw bounce indicator
            if (path[i].bounce) {
                this.ctx.stroke();
                this.ctx.fillStyle = '#ffaa00';
                this.ctx.beginPath();
                this.ctx.arc(path[i].x, path[i].y, 5, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.moveTo(path[i].x, path[i].y);
            }
        }
        
        this.ctx.stroke();
        
        // Draw ball hit indicator
        const lastPoint = path[path.length - 1];
        if (lastPoint.hitBall) {
            this.ctx.fillStyle = color;
            this.ctx.globalAlpha = 0.4;
            this.ctx.beginPath();
            this.ctx.arc(lastPoint.x, lastPoint.y, this.ballRadius * 2.5, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        this.ctx.globalAlpha = 1.0;
        this.ctx.setLineDash([]);
    }
    
    drawPredictions() {
        // Calculate direction from cue ball to mouse
        const aimDir = this.calculateDirection(this.cueBall, this.mousePos);
        
        if (aimDir.length < 10) return; // Don't draw if mouse is too close
        
        // Calculate max prediction distance
        const tableWidth = this.walls.right - this.walls.left;
        const tableHeight = this.walls.bottom - this.walls.top;
        const tableDiagonal = Math.sqrt(tableWidth * tableWidth + tableHeight * tableHeight);
        const maxPredictionDistance = tableDiagonal * this.predictionLengthMultiplier;
        
        // Draw prediction for each bounce level
        for (let b = 0; b <= this.maxBounces; b++) {
            const path = this.tracePath(this.cueBall, aimDir, maxPredictionDistance, b);
            const isDashed = b > 0;
            const colors = ['#00ff00', '#ffff00', '#ff8800', '#ff0088', '#8800ff', '#00ffff'];
            const color = colors[b % colors.length];
            this.drawPredictionLine(path, isDashed, color, b);
        }
    }
    
    updateStats() {
        const aimDir = this.calculateDirection(this.cueBall, this.mousePos);
        const angle = Math.atan2(aimDir.dy, aimDir.dx) * 180 / Math.PI;
        const statsDiv = document.getElementById('stats');
        statsDiv.textContent = `Aim angle: ${angle.toFixed(1)}° | Max bounces: ${this.maxBounces} | Prediction: ${this.predictionLengthMultiplier.toFixed(1)}x table diagonal`;
    }
    
    animate() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Draw table elements
        this.drawTable();
        this.drawPockets();
        
        // Draw predictions
        this.drawPredictions();
        
        // Draw balls
        this.targetBalls.forEach(ball => this.drawBall(ball));
        this.drawBall(this.cueBall);
        
        // Update stats
        this.updateStats();
        
        // Continue animation
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize the pool engine when the page loads
window.addEventListener('DOMContentLoaded', () => {
    const engine = new PoolEngine('poolTable');
});
