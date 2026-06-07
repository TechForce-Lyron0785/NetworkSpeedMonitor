# Deployment Guide – Network Speed Monitor v1.0

## Prerequisites
- Windows 10/11 (64-bit) or Windows Server 2016+
- No Python or Node.js required (single EXE)
- Administrator privileges (only for service installation, optional)

## Installation Methods

### Method 1: Portable (No Service)
Run the poller and API manually from USB drive.

1. Extract `speedmon.zip` to any folder (e.g., `D:\SpeedMonitor`).
2. Double-click `speedmon.exe`.
3. Open browser to `http://localhost:8000` to view dashboard.
4. The poller will run in the background. Close the console to stop.

### Method 2: Windows Service (Recommended for 24/7)
Runs automatically after reboot.

1. Extract `speedmon.zip` to `C:\Program Files\SpeedMonitor` (recommended).
2. Right-click `install.bat` → **Run as Administrator**.
3. The service will start automatically. Dashboard available at `http://localhost:8000`.
4. To uninstall: Run `uninstall.bat` as Administrator.

## Post-Installation Verification
- Open `http://localhost:8000/health` – should return JSON with "status":"ok".
- Wait 10 minutes, then open dashboard at `http://localhost:8000` (or `http://localhost:3000` if using separate React build). You should see data points appear.

## Firewall Notes
- The API listens on `localhost` only – no external access. No firewall changes needed.

## Logs
- If running as service: `C:\Program Files\SpeedMonitor\poller-stdout.log` and `api-stdout.log`.
- If running portable: `poller.log` in the same folder.

## Troubleshooting
See [known-issues.md](known-issues.md).

## Upgrading
- Stop the service (if installed).
- Replace `speedmon.exe` with new version.
- Restart service.