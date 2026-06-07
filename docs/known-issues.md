# Known Issues & Workarounds – Network Speed Monitor v1.0

## 1. WMI Query Fails on Windows LTSC / Older Versions
**Symptom:** Poller logs "WMI query failed" and falls back to psutil.
**Workaround:** Ensure your Windows version supports `PhysicalAdapter` property (Windows 8+). On older systems, the fallback works but may be less accurate.

## 2. Source Address Binding Fails on Some Network Drivers
**Symptom:** Speed tests return 0 Mbps even though adapter has IP.
**Cause:** Some network drivers don't support binding to a specific source IP.
**Workaround:** None currently. The poller will skip that cycle. Consider updating network drivers.

## 3. React Dashboard Shows "No Data" for Several Minutes
**Cause:** Poller interval is 3-5 minutes. Fresh install takes time.
**Workaround:** Wait 15 minutes after first start.

## 4. Windows Service Does Not Start Automatically After Reboot
**Symptom:** Services installed but not running after restart.
**Workaround:** Run `services.msc`, set startup type to Automatic (Delayed Start) for both services.

## 5. High CPU Usage (>5%) on Some Machines
**Cause:** Frequent polling or large database. Not common.
**Workaround:** Increase polling interval in config.json (future feature).

## 6. Conflict with Other Apps Using Port 8000
**Symptom:** API fails to start with "Address already in use".
**Workaround:** Change port in `backend/api/main.py` (update `uvicorn.run(port=8001)`) and update frontend `API_BASE`.