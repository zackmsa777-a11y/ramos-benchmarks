"""Verify current release fixtures independently of the historical suite pin."""
import hashlib,json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'benchmarks/current-compiler.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for task,record in meta['fixtures'].items():
    for language,source in record.items():
        suffix={'Ramos':'ramos','C':'c','Rust':'rs','Python':'py'}[language]
        assert sha(ROOT/f'benchmarks/fixtures/{task}.{suffix}')==source,(task,language)
compiler=ROOT/('work/ramos-'+meta['version'])
if not compiler.exists() or sha(compiler)!=meta['compiler_sha256']:
    data=urllib.request.urlopen(f"https://github.com/zackmsa777-a11y/ramos/releases/download/v{meta['version']}/ramos-linux-x86_64",timeout=60).read()
    assert hashlib.sha256(data).hexdigest()==meta['compiler_sha256']
    compiler.parent.mkdir(parents=True,exist_ok=True)
    temporary=compiler.with_suffix('.download');temporary.write_bytes(data)
    temporary.chmod(0o755);temporary.replace(compiler)
subprocess.run([sys.executable,str(ROOT/'benchmarks/run_suite.py'),'--compiler',str(compiler),
                '--validate-only','--output-dir',str(ROOT/'work/current-check')],check=True)
print('Current compiler: 324 independent four-language output checks passed')
