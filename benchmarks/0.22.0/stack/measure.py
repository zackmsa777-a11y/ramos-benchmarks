"""Paired native execution for the recursion-budget change; no language runtime."""
import argparse,hashlib,json,os,platform,random,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import run_suite as suite
OLD_SHA='e240393b8783023c6cc3a123a9961c98f2e3bfc74ef51d2df5de9914f8344e5b'
NEW_SHA='a034ea48f838c056c87c085450f0e96e727247b91f098d281f9ec4fa8cc801cc'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old',required=True,type=Path)
    parser.add_argument('--new',required=True,type=Path)
    parser.add_argument('--output-dir',type=Path,default=suite.ROOT/'work/stack-comparison')
    args=parser.parse_args()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    compilers={'old':args.old.resolve(),'new':args.new.resolve()}
    for name,expected in [('old',OLD_SHA),('new',NEW_SHA)]:
        assert sha(compilers[name])==expected,f'{name} compiler hash mismatch'
    inputs=Path(__file__).resolve().parents[1]/'results.json'
    workloads=json.loads(inputs.read_text())
    assert workloads['compiler_sha256']==NEW_SHA
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    work=suite.ROOT/'work/stack-paired';work.mkdir(parents=True,exist_ok=True)
    rng=random.Random(22021);tasks={}
    for task,record in workloads['tasks'].items():
        source=suite.FIXTURES/f'{task}.ramos'
        assert sha(source)==record['sources']['Ramos']['sha256']
        n,seed=record['work_count'],record['seed']
        expected=suite.reference(task,n,seed)
        assert f'{expected}\n'==record['expected_stdout']
        programs={name:work/f'{task}-{name}' for name in compilers}
        for name,compiler in compilers.items():
            suite.run([compiler,'build',source,'-o',programs[name],'--force'])
        for _ in range(2):
            for program in programs.values():suite.run([program,n,seed],expected)
        samples={'old':[],'new':[]};orders=[]
        for _ in range(9):
            order=list(programs);rng.shuffle(order);orders.append(order)
            for name in order:samples[name].append(suite.run([programs[name],n,seed],expected)[0])
        timings={name:suite.summarize(values) for name,values in samples.items()}
        tasks[task]={'work_count':n,'seed':seed,'expected_stdout':f'{expected}\n',
                     'source_sha256':sha(source),'timings':timings,'orders':orders,
                     'speedup':timings['old']['median_ns']/timings['new']['median_ns'],
                     'binary_sha256':{name:sha(program) for name,program in programs.items()}}
        print(task,tasks[task]['speedup'],flush=True)
    result={'measured_at_utc':datetime.now(timezone.utc).isoformat(),
        'environment':{'platform':platform.platform(), 'pinned_cpu':cpu,
                       'cpu_model':next(line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))},
        'workload_results_sha256':sha(inputs),
        'compilers':{name:{'sha256':sha(path),'version':suite.run([path,'--version'])[1].stdout.decode().strip()}
                     for name,path in compilers.items()},
        'settings':{'pinned_cpu':cpu,'samples':9,'warmups':2,'seed':22021},
        'tasks':tasks,'geomean_speedup':suite.geomean(t['speedup'] for t in tasks.values())}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Cost of deeper checked recursion: 0.21 / 0.22','',
        '| Task | 0.21 median ms | 0.22 median ms | 0.21 / 0.22 time |',
        '|---|---:|---:|---:|']
    for task,t in tasks.items():
        lines.append(f"| {task} | {t['timings']['old']['median_ns']/1e6:.3f} | {t['timings']['new']['median_ns']/1e6:.3f} | {t['speedup']:.3f} |")
    lines += ['',f"Equal-weight geometric mean of old/new median time: {result['geomean_speedup']:.3f}.",
        'A ratio below 1 means the new compiler took longer on these inputs.', '',
        'Nine paired rounds, randomized old/new order, two warmups, one pinned logical CPU.',
        'Each output matches the independent reference. Raw samples, variability, sources and',
        'binary/compiler hashes are in [results.json](results.json). This Linux VM sample',
        'does not establish Windows performance or universal speed. The new call/stack',
        'guards deliberately add checks to every generated function.', '',
        'Reproduce from the benchmark repository root with the verified release compilers:',
        '```sh','python benchmarks/0.22.0/stack/measure.py --old /path/to/ramos-0.21 --new /path/to/ramos-0.22 --output-dir work/stack-comparison','```','']
    (args.output_dir/'report.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
