# Cost of deeper checked recursion: 0.21 / 0.22

| Task | 0.21 median ms | 0.22 median ms | 0.21 / 0.22 time |
|---|---:|---:|---:|
| lcg | 46.031 | 41.744 | 1.103 |
| branches | 47.836 | 46.735 | 1.024 |
| gcd | 49.913 | 50.655 | 0.985 |
| recursive_tree | 138.474 | 140.902 | 0.983 |
| byte_hash | 50.313 | 48.167 | 1.045 |
| insertion_sort | 171.277 | 174.594 | 0.981 |
| matrix | 390.781 | 389.759 | 1.003 |
| text_scan | 106.507 | 108.628 | 0.980 |

Equal-weight geometric mean of old/new median time: 1.012.
A ratio below 1 means the new compiler took longer on these inputs.

Nine paired rounds, randomized old/new order, two warmups, one pinned logical CPU.
Each output matches the independent reference. Raw samples, variability, sources and
binary/compiler hashes are in [results.json](results.json). This Linux VM sample
does not establish Windows performance or universal speed. The new call/stack
guards deliberately add checks to every generated function.

Reproduce from the benchmark repository root with the verified release compilers:
```sh
python benchmarks/0.22.0/stack/measure.py --old /path/to/ramos-0.21 --new /path/to/ramos-0.22 --output-dir work/stack-comparison
```
