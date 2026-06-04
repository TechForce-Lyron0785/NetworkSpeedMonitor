# Test VM Setup

Use this guide to test NetworkSpeedMonitor inside a Windows guest VM. The
recommended local setup is VMware Workstation 16 Player with a Windows 10 or
later x64 guest.

## Current Test Environment

- Host: Windows PC with VMware Workstation 16 Player installed
- Guest: Windows 10 or later, x64
- Network mode: NAT or Bridged
- Python: 3.11 x64 recommended

## VMware Guest Settings

1. Shut down the VM.
2. In VMware Player, open **Player > Manage > Virtual Machine Settings**.
3. Confirm these settings:
   - **Memory**: 4 GB or more
   - **Processors**: 2 cores or more
   - **Network Adapter**: NAT or Bridged, with **Connect at power on** enabled
   - **Shared Folders**: optional, useful for sharing this repository with the
     guest
4. Start the VM.
5. Install VMware Tools inside the guest if it is not already installed.

NAT is usually easiest because the guest can reach the internet through the
host. Bridged mode is useful when you want the VM to appear as a separate
machine on the same LAN.

## Prepare Windows In The VM

1. Install Python 3.11 x64 from <https://www.python.org/downloads/windows/>.
2. During Python setup, enable **Add python.exe to PATH**.
3. Open PowerShell and verify Python:

```powershell
python --version
pip --version
```

4. Copy or clone this repository into the VM. For example:

```powershell
git clone <repo-url> C:\NetworkSpeedMonitor
cd C:\NetworkSpeedMonitor
```

If you use VMware Shared Folders instead, copy the project to a normal folder
inside the guest before testing. Running Python directly from a shared folder
can cause slower file access and permission surprises.

## Install Project Dependencies

From the repository root inside the VM:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the virtual environment again.

## Run The Test Suite

```powershell
pytest backend/tests/ -v
```

The current test suite includes a placeholder test, so this mainly confirms the
VM can import the project dependencies and run pytest.

## Run The Poller

```powershell
python backend\poller\poller.py
```

Stop it with `Ctrl+C`.

The poller writes logs to `poller.log` and stores samples through the backend
database layer.

## VMware Network Adapter Note

The poller tries to ignore virtual adapters when selecting a physical network
interface. Inside a VMware guest, the primary adapter may include `vmware` or a
VMware-specific name. If the poller logs this warning:

```text
No physical adapter found. Skipping cycle.
```

then the VM network is working, but the adapter selection logic is too strict
for a virtualized test environment. In that case, update the poller logic or add
a test-mode override so the VMware guest adapter can be selected.

## Quick Troubleshooting

- **No internet in the VM**: switch the VMware Network Adapter between NAT and
  Bridged, then reconnect it.
- **`python` is not recognized**: reinstall Python and enable **Add python.exe
  to PATH**, or use the Python Launcher with `py`.
- **Dependency install fails for `pywin32` or `wmi`**: confirm the guest uses
  x64 Python on Windows, then retry inside the activated virtual environment.
- **PowerShell cannot activate `venv`**: set the current-user execution policy
  to `RemoteSigned`.
- **Poller cannot find an adapter**: see the VMware network adapter note above.

## Cleanup Or Reset

For repeatable testing, take a VMware snapshot after Windows, VMware Tools,
Python, and project dependencies are installed. Restore that snapshot before
testing risky changes.
