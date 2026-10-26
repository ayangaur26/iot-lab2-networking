/**
 * Lab 2 Electron renderer — WiFi remote control.
 *
 * Edit DEFAULT_HOST to your Pi's IP, or use the IP field in the UI.
 */
const net = require("net");

const DEFAULT_HOST = "192.168.10.188";
const DEFAULT_PORT = 65432;
const STATUS_MS = 500;

let server_addr = DEFAULT_HOST;
let server_port = DEFAULT_PORT;
let busy = false;
let lastKeyCmd = null;

function saveHost() {
  const h = document.getElementById("serverHost").value.trim();
  const p = parseInt(document.getElementById("serverPort").value.trim(), 10);
  if (h) server_addr = h;
  if (!Number.isNaN(p) && p > 0) server_port = p;
  document.getElementById("raw").textContent = `Using ${server_addr}:${server_port}`;
}

function applyStats(obj) {
  const bat = obj.battery;
  document.getElementById("battery").textContent =
    bat === null || bat === undefined ? "N/A" : `${bat}%`;
  document.getElementById("moving").textContent = obj.moving || "—";
  document.getElementById("turning").textContent = obj.turning || "—";
  document.getElementById("speed").textContent =
    obj.speed !== undefined && obj.speed !== null ? Number(obj.speed).toFixed(2) : "—";
  document.getElementById("distance").textContent =
    obj.distance !== undefined && obj.distance !== null
      ? Number(obj.distance).toFixed(2)
      : "—";
  document.getElementById("temp").textContent =
    obj.temp_c === null || obj.temp_c === undefined ? "N/A" : `${obj.temp_c}`;
  document.getElementById("raw").textContent = JSON.stringify(obj);
}

function sendCommand(cmd, { updateUi = true } = {}) {
  return new Promise((resolve) => {
    // Skip overlapping status polls while a drive command is in flight
    if (busy && cmd === "status") {
      resolve(null);
      return;
    }
    const isDrive = cmd !== "status";
    if (isDrive) busy = true;

    const client = net.createConnection(
      { port: server_port, host: server_addr },
      () => {
        client.write(`${cmd}\n`);
      }
    );
    client.setTimeout(5000);

    let buf = "";
    const finish = (result) => {
      if (isDrive) busy = false;
      try {
        client.destroy();
      } catch (_) {}
      resolve(result);
    };

    client.on("data", (data) => {
      buf += data.toString();
    });
    client.on("end", () => {
      try {
        const line = buf.trim();
        if (line.startsWith("{")) {
          const obj = JSON.parse(line);
          if (updateUi) applyStats(obj);
          finish(obj);
        } else {
          document.getElementById("raw").textContent = buf;
          finish(null);
        }
      } catch (e) {
        document.getElementById("raw").textContent = `parse error: ${buf}`;
        finish(null);
      }
    });
    client.on("error", (err) => {
      document.getElementById("raw").textContent = `conn error: ${err.message}`;
      finish(null);
    });
    client.on("timeout", () => {
      document.getElementById("raw").textContent = "timeout";
      finish(null);
    });
  });
}

function setArrowActive(id, on) {
  const el = document.getElementById(id);
  if (!el) return;
  if (on) el.classList.add("active");
  else el.classList.remove("active");
}

function keyToCmd(e) {
  const k = e.key;
  if (k === "ArrowUp" || k === "w" || k === "W") return { cmd: "forward", id: "upArrow" };
  if (k === "ArrowDown" || k === "s" || k === "S") return { cmd: "backward", id: "downArrow" };
  if (k === "ArrowLeft" || k === "a" || k === "A") return { cmd: "left", id: "leftArrow" };
  if (k === "ArrowRight" || k === "d" || k === "D") return { cmd: "right", id: "rightArrow" };
  if (k === " " || k === "Escape") return { cmd: "stop", id: null };
  return null;
}

function updateKey(e) {
  const mapped = keyToCmd(e);
  if (!mapped) return;
  e.preventDefault();
  if (mapped.id) setArrowActive(mapped.id, true);
  if (lastKeyCmd === mapped.cmd) return;
  lastKeyCmd = mapped.cmd;
  sendCommand(mapped.cmd);
}

function resetKey(e) {
  const mapped = keyToCmd(e);
  ["upArrow", "downArrow", "leftArrow", "rightArrow"].forEach((id) =>
    setArrowActive(id, false)
  );
  if (!mapped) return;
  e.preventDefault();
  lastKeyCmd = null;
  sendCommand("stop");
}

document.onkeydown = updateKey;
document.onkeyup = resetKey;

window.sendCommand = sendCommand;
window.saveHost = saveHost;

// Periodic status poll (not 50ms — that floods the Pi)
setInterval(() => {
  if (!busy) sendCommand("status");
}, STATUS_MS);

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("serverHost").value = server_addr;
  document.getElementById("serverPort").value = String(server_port);
  sendCommand("status");
});
