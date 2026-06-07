# Release Checklist v1.0.0

## Pre-Build
- [ ] All unit tests pass (`pytest backend/tests/`)
- [ ] Integration test passes (`python scripts/integration_test.py`)
- [ ] No linting errors (flake8, ESLint)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Database schema is up-to-date
- [ ] Version number updated in code (if any)

## Build (PyInstaller)
- [ ] React build copied to `backend/api/static/`
- [ ] PyInstaller spec file configured
- [ ] `speedmon.exe` builds without errors
- [ ] `speedmon.exe` size < 50 MB

## Packaging
- [ ] `speedmon.zip` contains: `speedmon.exe`, `install.bat`, `uninstall.bat`, `nssm.exe`, `README.txt`
- [ ] Zip file size < 30 MB

## Test on Clean Windows VM (VMware)
- [ ] VM has no Python, no Node.js
- [ ] Copy zip to VM, extract, run portable EXE – dashboard loads
- [ ] Run `install.bat` as Administrator – services created and start
- [ ] After 30 minutes, data appears in dashboard
- [ ] Uninstall removes services cleanly
- [ ] Test with active VPN – speeds match physical ISP

## Test on USB Drive
- [ ] Copy `speedmon.zip` to FAT32/NTFS USB drive
- [ ] Extract on another machine, run EXE from USB – works

## Deployment to Production Target Machine
- [ ] Target machine meets requirements (Windows 10/11)
- [ ] Copy zip, extract, run installer (or portable)
- [ ] Dashboard accessible within 2 seconds
- [ ] Poller collects data for 1 hour without crash

## Post-Deployment Monitoring (24h)
- [ ] Health endpoint returns `"status":"ok"`
- [ ] Database has samples for each 3-5 minute interval
- [ ] Memory usage < 30 MB after 24h
- [ ] No crash or service stop

## Go/No-Go Decision
- [ ] All above passed → **RELEASE**