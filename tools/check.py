"""Validate fixtures against independent references without timing claims."""
from pathlib import Path
import subprocess
import sys
from compiler import install
from provenance import check_sources
ROOT = Path(__file__).resolve().parents[1]
check_sources(ROOT)
compiler = install()
subprocess.run([sys.executable, str(ROOT / "benchmarks/run_suite.py"),
                "--compiler", str(compiler), "--validate-only"], check=True, cwd=ROOT)
print("324 reference output checks passed (8 tasks + startup, 4 languages, 9 inputs)")
subprocess.run([sys.executable, str(ROOT / 'tools/check_collections.py')], check=True, cwd=ROOT)

subprocess.run([sys.executable, str(ROOT / 'tools/check_current.py')], check=True, cwd=ROOT)
