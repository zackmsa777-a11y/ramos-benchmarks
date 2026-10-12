"""Measure native int-list growth/reservation; report checksums and managed bytes."""
from pathlib import Path
import argparse, hashlib, json, platform, statistics, subprocess, tempfile, time
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compiler', required=True)
parser.add_argument('--samples', type=int, default=9)
parser.add_argument('--count', type=int, default=131072)
parser.add_argument('--cycles', type=int, default=24)
parser.add_argument('--output', default='work/collections.json')
parser.add_argument('--validate-only', action='store_true')
args = parser.parse_args()
if platform.system() != 'Linux': parser.error('Timing methodology targets Linux x64')
if not 1 <= args.count <= 131072 or not 1 <= args.cycles <= 1000 or not 1 <= args.samples <= 99:
    parser.error('count=1..131072, cycles=1..1000, samples=1..99')
compiler = Path(args.compiler).resolve()
version = subprocess.check_output([str(compiler),'--version'],text=True).strip()
if not version.startswith('Ramos 0.21.'): parser.error('Use the 0.21 Linux compiler')
output = Path(args.output).resolve()
if output.is_relative_to(HERE): parser.error('Fresh results belong under work/, not archived evidence')
sha = lambda data: hashlib.sha256(data).hexdigest()
variants = [('legacy-growth','legacy',False), ('current-growth','current',False), ('current-reserved','current',True)]
results = {name:{'wall_ms':[]} for name,_,_ in variants}
with tempfile.TemporaryDirectory(prefix='ramos-collections-') as temp:
    root = Path(temp); binaries = {}
    for name, snapshot, reserved in variants:
        source = root/(name+'.ramos')
        library = root/(snapshot+'.ramos');library.write_bytes((HERE/snapshot/'lists.ramos').read_bytes())
        reserve = 'list_reserve(values, count)' if reserved else ''
        source.write_text(f'''weave "{snapshot}.ramos"
fn fill(count: int64) -> int64 {{
    let values = list_new()
    {reserve}
    var total = 0
    for i in 0..count {{ list_push(values, i) }}
    for i in 0..count {{ total += list_get(values, i) }}
    return total
}}
fn main() {{
    var total = 0
    for round in 0..{args.cycles} {{
        total += fill({args.count})
        collect()
    }}
    print(total)
    let values = list_new()
    {('list_reserve(values, '+str(args.count)+')') if reserved else ''}
    for i in 0..{args.count} {{ list_push(values, i) }}
    print(memory_used())
    collect()
    print(memory_used())
    list_clear(values)
    collect()
    print(memory_used())
    {('list_release(values)') if snapshot=='current' else 'values.data = array_empty(int64)'}
    collect()
    print(memory_used())
}}
''')
        binary = root/name
        subprocess.run([str(compiler),'build',str(source),'-o',str(binary)],check=True)
        binaries[name] = binary
    samples = 1 if args.validate_only else args.samples
    expected = args.cycles * args.count * (args.count-1)//2
    for index in range(samples+1):
        # First round is an unreported warm-up; rotate order to reduce ordering bias.
        order = variants[index % 3:]+variants[:index % 3]
        for name,_,_ in order:
            start = time.perf_counter()
            completed = subprocess.run([str(binaries[name])],capture_output=True,timeout=60)
            elapsed = (time.perf_counter()-start)*1000
            assert completed.returncode==0, completed.stderr
            lines = list(map(int,completed.stdout.splitlines()))
            assert len(lines)==5 and lines[0]==expected, (name,lines)
            assert lines[3] >= args.count*8 and lines[4] < 65536, (name,lines)
            if index:
                results[name]['wall_ms'].append(elapsed)
                results[name]['managed_bytes'] = dict(zip(['after_fill','after_collect','after_clear_collect','after_release_collect'],lines[1:]))
for row in results.values():
    row['median_ms'] = statistics.median(row['wall_ms'])
    row['minimum_ms'] = min(row['wall_ms']);row['maximum_ms'] = max(row['wall_ms'])
report = {'version':version, 'compiler_sha256':sha(compiler.read_bytes()),
          'machine':platform.platform(), 'cpu':next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')), 'unknown'),
          'count':args.count,'cycles':args.cycles,'samples':samples,'expected_checksum':expected,
          'libraries':{snapshot:sha((HERE/snapshot/'lists.ramos').read_bytes()) for snapshot in ['legacy','current']},
          'results':results,
          'notes':'All variants compiled with one 0.21 compiler; total wall time includes startup, pushes, reads, GC and a memory fixture; no C/Rust/Python execution comparison. Legacy release uses direct array detachment because its library lacks release.'}
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{'median_ms':round(v['median_ms'],3),'managed_bytes':v['managed_bytes']} for k,v in results.items()},indent=2))
print(output)
