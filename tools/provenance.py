from pathlib import Path
import hashlib
import json

def check_sources(root):
    pin = json.loads((root / "upstream.json").read_text())
    adapted = pin.get("adaptations", {})
    for item in pin["files"]:
        path = root / item["path"]
        expected = adapted.get(item["path"], {}).get("sha256", item["sha256"])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    print(f"Verified {len(pin['files'])} pinned/adapted source hashes", flush=True)
