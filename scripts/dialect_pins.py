"""Resolve published sibling inputs only at the commits recorded in gate.toml."""
from functools import lru_cache
import os
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=None)
def sibling(name, root=ROOT):
    root = Path(root)
    pins = tomllib.loads((root / 'gate.toml').read_text())['siblings']
    if name not in pins:
        raise RuntimeError(f'gate.toml has no pin for {name}')
    sha = pins[name]['sha']
    layout = os.environ.get('BENNETT_GATE_LAYOUT')
    path = (Path(layout) / name if layout else
            root / '.tmp/gate/cache' / f'{name}@{sha[:12]}' / name)
    result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True)
    actual = result.stdout.strip() if result.returncode == 0 else 'missing checkout'
    if actual != sha:
        raise RuntimeError(f'{name}: gate.toml pin {sha}; actual {actual} at {path}; materialise the gate pin')
    dirty = subprocess.run(['git', '-C', str(path), 'diff', '--quiet', 'HEAD', '--'],
                           capture_output=True, text=True)
    if dirty.returncode:
        raise RuntimeError(f'{name}: pinned checkout {sha} has modified tracked files at {path}')
    return path.resolve()
