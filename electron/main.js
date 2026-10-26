// Electron main process — Lab 2 remote control UI
const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 720,
    webPreferences: {
      nodeIntegration: true, // needed for require('net') in index.js
      contextIsolation: false, // lab note — allow renderer net sockets
      preload: path.join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadFile("index.html");
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", function () {
  app.quit();
});
