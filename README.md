# Ramos benchmarks

Reproducible fixtures and historical evidence comparing **Ramos, C, Rust and
Python**, plus focused Ramos before/after workloads. Part of the
[Ramos project hub](https://github.com/zackmsa777-a11y/ramos/blob/main/docs/ecosystem.md).
The eight-task suite now accepts the pinned **Ramos 0.20.0** compiler.

## Validate before measuring

Use Linux x64 with Python 3, GCC and Rust (`rustc`) installed. Download the
[0.20.0 Linux compiler](https://github.com/zackmsa777-a11y/ramos/releases/tag/v0.20.0)
as `ramos` and make it executable, or install it with its SHA-256 check:

```sh
python tools/compiler.py
python tools/check.py
```

The check verifies copied/adapted source hashes, builds all native variants and
compares 324 outputs with independent references: eight tasks plus startup,
four languages, three work counts and three seeds. It creates no timing claim.
The timing runner is Linux-only; Windows compiler support does not imply a
portable timing methodology or comparable results.

## Measure a fresh run

```sh
python benchmarks/run_suite.py --compiler ./ramos --samples 9 --output-dir work/current
```

This calibrates work counts and publishes `report.md` and raw `results.json`.
Compare releases using the same work counts:

```sh
python benchmarks/run_suite.py --compiler ./ramos --work-counts benchmarks/0.14.0/results.json --output-dir work/current-fixed
python benchmarks/compare_versions.py --baseline-compiler /absolute/path/to/older/ramos --output-dir work/comparison
```

Fresh reports default to ignored `work/results/`; comparisons to `work/comparisons/`.
They never replace the committed historical reports by default. For optional
plots install matplotlib and pass an explicit output under `work/`:

```sh
python benchmarks/plot_results.py --results work/current/results.json --output work/current/score.png
```

## The index

The eight tasks cover serial arithmetic/modulo, branches, GCD, a recursive
tree, byte hashing, insertion sort, matrix multiplication and text scanning. See the actual
fixture names and equations in [run_suite.py](benchmarks/run_suite.py).
The performance index normalizes **C to 100** and takes the geometric mean of
per-task throughput ratios. Higher means faster for these workloads only.
It is not a language-quality score and does not predict every application's speed.
Runtime arithmetic/bounds checks, build commands, calibration, raw samples,
compiler hashes, machine and toolchain versions remain in the generated report.
Never combine unrelated versions or machines into one claimed current score.

## Preserved evidence

| Evidence | Origin/version |
| --- | --- |
| [Early microbenchmark](benchmarks/report-0.2.md) | 0.2 kernel experiment; narrow historical scope |
| [Eight-task baseline](benchmarks/baseline-0.7.0/report.md) | 0.7.0 |
| [Eight-task report](benchmarks/report.md) | Historical report; read its version and machine labels |
| [0.14 evidence](benchmarks/0.14.0/report.md) | Eight-task suite and range-loop work |
| [Text-builder workload](benchmarks/0.17.0/text-builder.md) | One focused text-building workload, not an overall score |

Copied fixtures, reports, JSON and images remain byte-identical to the upstream
commit in [upstream.json](upstream.json). Two orchestration scripts and the optional plot generator are adapted: accept
0.20, place fresh reports under `work/`, use standalone reproduction commands
and label new reports with their actual compiler versions and host. The original
hashes and adaptation hashes are recorded. These old measurements are not new
0.20.0 measurements. New optimization claims require fresh data and compiler
correctness/self-hosting checks in the source repository.

The compiler repository retains historical release/test copies for compatibility;
new benchmark development and published runs belong here. The pinned `stdlib/`
is used by the text-builder workload. No runtime backend is delegated.

## Ramos family

[Source](https://github.com/zackmsa777-a11y/ramos) ·
[Book](https://github.com/zackmsa777-a11y/ramos-docs) ·
[Examples](https://github.com/zackmsa777-a11y/ramos-examples) ·
[Calculator](https://github.com/zackmsa777-a11y/ramos-calculator) ·
[Benchmarks](https://github.com/zackmsa777-a11y/ramos-benchmarks)

Browse the shared [Ramos topic](https://github.com/topics/ramos).

## rmatrix application workload

[0.20.0 terminal rendering report](benchmarks/0.20.0/rmatrix/report.md) preserves
before/after sources, raw PTY results and a self-contained reproduction runner.
It measures application output and pacing, separately from the eight-task index.

[0.21 collection workload](benchmarks/0.21.0/collections/report.md) compares
normal growth, reservation and explicit release with source snapshots and raw
samples. It uses a separately verified 0.21 compiler; the existing suite's 0.20
pin and historical rmatrix reproduction commands remain valid. Reservation
reduces observed allocated bytes in the fixture; no speed gain is established.
