// Electron main process - Desktop overlay application
const { app, BrowserWindow, screen, globalShortcut, ipcMain } = require('electron');
const path = require('path');

let overlayWindow = null;
let isOverlayVisible = false;

function createOverlay() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    
    overlayWindow = new BrowserWindow({
        width: width,
        height: height,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        skipTaskbar: false,
        resizable: false,
        movable: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });
    
    // Enable click-through when not in setup mode
    overlayWindow.setIgnoreMouseEvents(true, { forward: true });
    
    overlayWindow.loadFile('overlay.html');
    
    // Open DevTools for debugging (remove in production)
    // overlayWindow.webContents.openDevTools({ mode: 'detach' });
    
    overlayWindow.on('closed', () => {
        overlayWindow = null;
    });
    
    // Start hidden
    overlayWindow.hide();
}

app.whenReady().then(() => {
    createOverlay();
    
    // Global hotkey to toggle overlay (Ctrl+Shift+P)
    globalShortcut.register('CommandOrControl+Shift+P', () => {
        if (overlayWindow) {
            if (isOverlayVisible) {
                overlayWindow.hide();
                isOverlayVisible = false;
            } else {
                overlayWindow.show();
                overlayWindow.setAlwaysOnTop(true, 'screen-saver');
                isOverlayVisible = true;
            }
        }
    });
    
    // Global hotkey to quit app (Ctrl+Shift+Q)
    globalShortcut.register('CommandOrControl+Shift+Q', () => {
        app.quit();
    });
});

// IPC handlers
ipcMain.on('setup-mode-changed', (event, isSetupMode) => {
    if (overlayWindow) {
        // Enable mouse events during setup, disable otherwise
        overlayWindow.setIgnoreMouseEvents(!isSetupMode, { forward: true });
    }
});

ipcMain.on('minimize-app', () => {
    if (overlayWindow) {
        overlayWindow.hide();
        isOverlayVisible = false;
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (overlayWindow === null) {
        createOverlay();
    }
});

app.on('will-quit', () => {
    globalShortcut.unregisterAll();
});
