import subprocess
import time
import requests
import os


def run_command(cmd, cwd=None):
    proc = subprocess.Popen(
        cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout.decode(), stderr.decode()


def test_poller_install():
    print("Testing service installation...")
    os.chdir("scripts")
    ret, out, err = run_command("install.bat")
    time.sleep(5)
    # Check if services exist
    ret2, out2, _ = run_command("sc query SpeedMonitor-Poller")
    if "RUNNING" in out2:
        print("✅ Poller service running")
    else:
        print("❌ Poller service not running")
    return "RUNNING" in out2


def test_api_endpoints():
    print("Testing API endpoints...")
    time.sleep(10)  # wait for API to start
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        if r.status_code == 200:
            print("✅ API health endpoint OK")
        else:
            print("❌ API health failed")
            return False
        # Test daily endpoint
        r2 = requests.get("http://localhost:8000/daily?date=2026-06-04")
        if r2.status_code == 200:
            print("✅ /daily OK")
        else:
            print("❌ /daily failed")
        return True
    except Exception as e:
        print(f"API unreachable: {e}")
        return False


def test_dashboard_build():
    print("Building React dashboard...")
    os.chdir("../frontend")
    ret, out, err = run_command("npm run build")
    if ret == 0:
        print("✅ React build successful")
        return True
    else:
        print(f"❌ Build failed: {err}")
        return False


def main():
    print("===== Regression Test Suite =====")
    test_poller_install()
    test_api_endpoints()
    test_dashboard_build()
    print("===== Regression Test Complete =====")


if __name__ == "__main__":
    main()