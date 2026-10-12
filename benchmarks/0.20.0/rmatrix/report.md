# rmatrix rendering and timing — Ramos 0.20.0

Measured on 12 October 2026, Linux x64. Both source snapshots were compiled
with the same native Ramos 0.20.0 compiler to isolate the application changes.
The [upstream nmatrix MIT notice](LICENSE.nmatrix) is retained with the port.
See [raw results](results.json), [provenance and source hashes](provenance.json),
and the preserved [before](baseline/rmatrix.ramos)/[after](candidate/rmatrix.ramos) sources.

| Scene | Before FPS | After FPS | Before MiB/s | After MiB/s |
| --- | ---: | ---: | ---: | ---: |
| rain | 55.00 | 59.76 | 1.308 | 0.181 |
| spiral | 53.59 | 59.84 | 0.726 | 0.182 |
| plasma | 48.32 | 59.85 | 2.458 | 0.251 |
| blackhole | 52.05 | 59.76 | 0.726 | 0.165 |

Plasma emitted about **90% fewer bytes per second** while approaching its
requested 60 FPS in this fast-reader sample. At a simulated 0.5 MiB/s reader
cap, plasma changed from 9.60 to 60.10 observed FPS; after-change P95 delivery
interval was 27.85 ms. This does not establish perfectly smooth visible 60 FPS.

## Method and limits

The Linux PTY was 160 columns × 61 rows, with a 160×60 render grid, seed 42,
`--no-name` and target 60 FPS. Each scene/version has one three-second sample.
The harness consumes ANSI output without painting pixels. A test-only OSC marker
after each grid emission supplies frame delivery timestamps. Buffering can
combine deliveries; reported intervals exclude zero-length intervals. Requested
FPS, emitted frames, delivered frames and visible terminal paint are different
quantities. These short samples show the bottleneck and improvement, not a
statistical confidence interval or a language-wide Rust/C comparison. The
read cap is a simulation, not a measured SSH connection or terminal bandwidth.

The old app waited a full frame interval after work and advanced simulation by
frame count. The new app includes work in the deadline and advances from actual
elapsed time. Scene state at the same frame number consequently differs.
Changed-cell output, cached HUD, direct byte output and idle handling reduce
output; explicit ANSI intensity resets also fix a bold/faint state leak.

The paused sample contains startup and the pause transition. Its candidate
`observed_fps` of 79.22 is based on only five transient frames and is **not a
paused frame rate**. A separate settled PTY integration check confirmed zero
output for 0.3 seconds while paused. CPU/RSS are brief observations, not a
long-running memory guarantee. Real terminals can still be slower. No Windows
animation performance was measured.

## Reproduce

From the benchmark repository root, use Linux x64 and the pinned compiler:

```sh
python tools/compiler.py
python benchmarks/0.20.0/rmatrix/measure.py --compiler ./ramos --output work/rmatrix.json
```

The runner copies preserved sources into a temporary directory, adds the marker
to both versions, builds native executables and records fresh measurements. It
requires a compiler whose hash/version match provenance. It never overwrites
this historical result file. Each snapshot includes its reviewed library files
so its relative weave paths are self-contained. Python is measurement tooling;
the applications and renderers run entirely in native Ramos.

## Correctness checks

The [published project](https://github.com/zackmsa777-a11y/ramos-examples/tree/main/projects/rmatrix)
compares 40 deterministic screen/style frames across all eight palettes and
echo, pulse and scanline combinations. Its full-grid reference includes the
explicit intensity reset so the intended ANSI style has a defined baseline.
Actual Linux PTY checks cover all twelve scenes, controls, overlays, paused
silence, resize recovery, HUD toggling, resume and Ctrl+C cleanup. Both targets
build; native Windows CI checks the renderer and noninteractive CLI. Interactive
Windows rmatrix controls remain to be checked on a real Windows terminal.
