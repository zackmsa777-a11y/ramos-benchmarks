"""Install the pinned native Ramos compiler; no application runtime dependency."""
from pathlib import Path
import hashlib
import platform
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.19.1"
ASSETS = {
    "Linux": ("ramos-linux-x86_64", "ramos", "1da8f6e6f28144cdad98ab6a2fe8cea138d7c3f02191175c191933964324007b"),
    "Windows": ("ramos.exe", "ramos.exe", "dda862f14f4c6d9cea41875ed4aa60f7a101bbbc1cd56c66c3c861fa94a9e222"),
}

def install():
    system = platform.system()
    if platform.machine().lower() not in ("x86_64", "amd64") or system not in ASSETS:
        raise SystemExit("Ramos 0.19.1 requires Linux x64 or Windows x64")
    asset, filename, sha = ASSETS[system]
    path = ROOT / filename
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == sha:
        return path
    url = f"https://github.com/zackmsa777-a11y/ramos/releases/download/v{VERSION}/{asset}"
    data = urllib.request.urlopen(url, timeout=60).read()
    if hashlib.sha256(data).hexdigest() != sha:
        raise SystemExit("Compiler SHA-256 mismatch; installation aborted")
    temporary = path.with_suffix(".download")
    temporary.write_bytes(data)
    temporary.chmod(0o755)
    temporary.replace(path)
    return path

if __name__ == "__main__":
    print(install())
