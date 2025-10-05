// Preload script for Electron security
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    setSetupMode: (isSetupMode) => ipcRenderer.send('setup-mode-changed', isSetupMode),
    minimizeApp: () => ipcRenderer.send('minimize-app')
});
