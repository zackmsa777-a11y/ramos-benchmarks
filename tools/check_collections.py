"""Validate the 0.21 fixture independently of the historical 0.20 suite pin."""
from pathlib import Path
import hashlib,json,subprocess,sys,urllib.request
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'benchmarks/0.21.0/collections'
meta=json.loads((HERE/'results.json').read_text())
sha=lambda data:hashlib.sha256(data).hexdigest()
for name,expected in meta['libraries'].items():
    assert sha((HERE/name/'lists.ramos').read_bytes())==expected,name
compiler=ROOT/'work/ramos-0.21.0'
if not compiler.exists() or sha(compiler.read_bytes())!=meta['compiler_sha256']:
    data=urllib.request.urlopen('https://github.com/zackmsa777-a11y/ramos/releases/download/v0.21.0/ramos-linux-x86_64',timeout=60).read()
    assert sha(data)==meta['compiler_sha256'],'Compiler SHA-256 mismatch'
    compiler.parent.mkdir(parents=True,exist_ok=True)
    temporary=compiler.with_suffix('.download');temporary.write_bytes(data)
    temporary.chmod(0o755);temporary.replace(compiler)
subprocess.run([sys.executable,str(HERE/'run.py'),'--compiler',str(compiler),'--validate-only',
                '--output',str(ROOT/'work/collections-check.json')],check=True)
print('Collection fixture checksums and clear/release memory invariants passed')
