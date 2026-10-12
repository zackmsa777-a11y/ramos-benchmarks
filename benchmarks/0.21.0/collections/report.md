# Integer collection controls — Ramos 0.21.0

Measured on 12 October 2026, Linux x64. [Raw samples](results.json),
[source provenance](provenance.json), [legacy library](legacy/lists.ramos),
[current library](current/lists.ramos) and [runner](run.py) are retained.
All variants use the same native 0.21.0 compiler to isolate library behavior.

Each sample fills and reads 131072 integers 24 times, checks the sum, requests
collection between cycles and then runs a managed-memory fixture. Nine timed
samples per variant follow an unreported warm-up; variant order rotates.
Wall time includes startup, pushes, reads, collection and the final memory
fixture. It is not a push-only latency, peak RSS or language-wide speed index.

| Variant | Median ms | Allocated bytes after final fill | Bytes after clear + collect | Bytes after release + collect |
| --- | ---: | ---: | ---: | ---: |
| Legacy growth | 146.03 | 4194928 | 1048656 | 80 |
| Current growth | 147.87 | 4194928 | 1048656 | 80 |
| Current reservation | 152.58 | 3145952 | 1048656 | 80 |

The normal growth path remains close to the legacy workload. Reservation
reduces the observed allocated-block count here but **does not establish a
speed improvement**: its median is slower in these samples. Reserve is useful
when size is known and intermediate growth/copies should be avoided, not as a
promise that every workload will run faster. The raw min/max values and all
individual samples are retained; no statistical confidence interval is claimed.

Both versions retain approximately 1 MiB when clearing the full list. The new
`list_release` makes storage detachment an explicit helper and leaves an 80-byte
list after collection in this fixture. The legacy fixture manually assigns an
empty backing array for the same comparison; this was not a legacy release API.
`memory_used()` counts allocated headers/padding and uncollected garbage,
including conservatively retained data. These snapshots are not heap high-water
marks, exact process-memory measurements or guarantees for arbitrary aliases.
Retained backing-array aliases deliberately remain valid and can keep storage
alive. The 16 MiB live heap and 131072-element limits are unchanged.

## Reproduce

Use Linux x64. Download the **0.21.0** native compiler separately; this repository's
existing eight-task and rmatrix pin remains 0.20.0 for historical compatibility:

```sh
mkdir -p work
curl -L https://github.com/zackmsa777-a11y/ramos/releases/download/v0.21.0/ramos-linux-x86_64 -o work/ramos-0.21.0
chmod +x work/ramos-0.21.0
python benchmarks/0.21.0/collections/run.py --compiler work/ramos-0.21.0 --output work/collections-fresh.json
```

Verify the compiler's SHA-256 against this report's raw metadata or the release
checksum file. Fresh results go under `work/`; the runner refuses to overwrite
archived evidence. `--validate-only` checks reference sums and memory-fixture
invariants without establishing a timing claim. Python is orchestration only;
all workload code and collection operations run natively in Ramos.

## Correctness and scope

Native Linux and Windows corpus tests cover reserve statuses, odd-capacity
growth capped at the array maximum, rejection without mutation, full-map
replacement, aliases and independently checked integer sorting. Repeated
list/map clear/release cycles allocate more than the cumulative heap limit and
remain within their checked live-memory bounds. `rsort` exercises stdin, streamed
Unicode paths, signed extremes, malformed input and exact/excess collection
capacity. The compiler still reaches both native fixed points.
Maps remain linear lookup; these results do not claim a hash-map improvement,
new allocator, larger heap, general collections, or faster sorting than C/Rust.
