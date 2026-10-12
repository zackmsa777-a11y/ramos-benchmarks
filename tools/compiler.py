"""Install the pinned native Ramos compiler; no application runtime dependency."""
from pathlib import Path
import hashlib
import platform
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.20.0"
ASSETS = {
    "Linux": ("ramos-linux-x86_64", "ramos", "47458291597a36eae9ddbbed0268cf3bab5480d6238ecef00f1e96ae733f39ba"),
    "Windows": ("ramos.exe", "ramos.exe", "0f14383b16e541b71e0606df262848e14bc0269bd0e3dee84ba914ab9a90c353"),
}

def install():
    system = platform.system()
    if platform.machine().lower() not in ("x86_64", "amd64") or system not in ASSETS:
        raise SystemExit("Ramos 0.20.0 requires Linux x64 or Windows x64")
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
