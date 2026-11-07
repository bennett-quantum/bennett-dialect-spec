"""Record snapshot builds without compiling an unrelated Rust fixture crate."""
from pathlib import Path


def record_build(argv, **_options):
    if list(argv[:3]) != ['cargo', 'build', '--release']:
        raise AssertionError(f'unexpected command in snapshot build test: {argv}')
    manifest = Path(argv[argv.index('--manifest-path') + 1])
    target = Path(argv[argv.index('--target-dir') + 1])
    executable = target / 'release/bennett-isa-ref'
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_text((manifest.parent / 'src/main.rs').read_text())
    return ''
