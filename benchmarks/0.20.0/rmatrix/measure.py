"""Linux-only rmatrix before/after measurement; preserve archived results."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
import probe

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compiler', required=True)
parser.add_argument('--output', default='work/rmatrix.json')
parser.add_argument('--seconds', type=float, default=3)
args = parser.parse_args()
if platform.system() != 'Linux':
    parser.error('The PTY and /proc methodology requires Linux')
if not .2 <= args.seconds <= 60:
    parser.error('seconds must be between 0.2 and 60')
compiler = Path(args.compiler).resolve()
provenance = json.loads((HERE/'provenance.json').read_text())
if hashlib.sha256(compiler.read_bytes()).hexdigest() != provenance['compiler_sha256']:
    parser.error('Use the exact 0.20.0 Linux compiler recorded in provenance.json')
for path, expected in provenance['sources'].items():
    assert hashlib.sha256((HERE/path).read_bytes()).hexdigest() == expected, path
output = Path(args.output).resolve()
if output.is_relative_to(HERE):
    parser.error('Use work/ for new results; archived evidence is immutable')
marker = '''    let frame_marker = bytes_copy("X]777;rmatrix-frameX")
    buffer_set(frame_marker, 0, 27)
    buffer_set(frame_marker, buffer_len(frame_marker) - 1, 7)
'''
results = []
with tempfile.TemporaryDirectory(prefix='rmatrix-measure-') as temp:
    work = Path(temp)
    probe.ROOT = work
    for version in ['baseline', 'candidate']:
        source = work/version
        shutil.copytree(HERE/version, source)
        main = source/'rmatrix.ramos'
        text = main.read_text()
        assert text.count('fn main() {') == 1
        text = text.replace('fn main() {\n', 'fn main() {\n'+marker, 1)
        lines = text.splitlines(keepends=True)
        found = 0
        for index in range(len(lines)-1,-1,-1):
            if lines[index].lstrip().startswith('emit_grid('):
                lines.insert(index+1, '            stdout(frame_marker)\n')
                found += 1
        assert found == 1
        main.write_text(''.join(lines))
        binary = work/(version+'-marked')
        subprocess.run([str(compiler),'build',str(main),'-o',str(binary)],check=True)
        for mode in ['rain','spiral','plasma','blackhole']:
            row = probe.probe(mode,160,61,seconds=args.seconds,binary=str(binary))
            row['version'] = version
            results.append(row)
        for mode, cap, keys, seconds in [('plasma',512*1024,b'',args.seconds),
                                        ('rain',None,b' ',min(2,args.seconds))]:
            row = probe.probe(mode,160,61,seconds=seconds,binary=str(binary),
                              bytes_per_second=cap,keys=keys)
            row['version'] = version
            results.append(row)
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(results,indent=2)+'\n')
print('Fresh samples:',output)
