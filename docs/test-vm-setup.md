# Test VM Setup

## Hardware Requirements
- Windows 10/11 Pro or Enterprise (for Sandbox) or any edition with VirtualBox.

## Steps for Windows Sandbox (easiest)
1. Enable Windows Sandbox.
2. Create `sandbox-config.wsb` with:
```xml
<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\path\to\NetworkSpeedMonitor</HostFolder>
      <SandboxFolder>C:\SpeedMonitor</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell -command "cd C:\SpeedMonitor; python backend\poller\poller.py"</Command>
  </LogonCommand>
</Configuration>