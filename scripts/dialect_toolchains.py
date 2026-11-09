"""Read the legality toolchain inventory using the invoking user's HOME."""
import os
from pathlib import Path
import re
import shlex
import tomllib


def load_toolchains(path):
    config = tomllib.loads(Path(path).read_text())
    if not config:
        raise ValueError(f'{path}: no LLVM toolchains declared')
    for section, entry in config.items():
        if not re.fullmatch(r'llvm\d+', section) or not isinstance(entry, dict):
            raise ValueError(f'{path}: invalid toolchain section {section}')
        if 'bin' not in entry or entry.keys() - {'bin', 'frontend_bin'}:
            raise ValueError(f'{path}.{section}: expected bin and optional frontend_bin')
        for field, value in entry.items():
            if not isinstance(value, str) or not value:
                raise ValueError(f'{path}.{section}.{field}: expected a nonempty directory path')
            if value.startswith('$HOME/'):
                if not os.environ.get('HOME'):
                    raise ValueError(f'{path}.{section}.{field}: HOME is unset; set HOME to resolve {value}')
                value = str(Path(os.environ['HOME']) / value[len('$HOME/'):])
            directory = Path(value)
            if not directory.is_absolute() or '$' in value:
                raise ValueError(f'{path}.{section}.{field}: expected an absolute or $HOME/ directory, got {value!r}')
            entry[field] = directory
    return config


def provision_toolchain(directory, major):
    value = str(directory)
    if '.rustup/toolchains/' in value:
        toolchain = value.split('.rustup/toolchains/', 1)[1].split('/', 1)[0]
        return shlex.join(['rustup', 'component', 'add', 'llvm-tools', '--toolchain', toolchain])
    if '.julia/artifacts/' in value and str(major) == '20':
        project = Path(os.environ['HOME']) / '.local/share/bennett-llvm20'
        return shlex.join(['julia', f'--project={project}', '-e',
                          'using Pkg; Pkg.add(PackageSpec(name="LLVM_full_jll", version="20.1.8"))'])
    return shlex.join(['sudo', 'apt-get', 'install', '-y', f'clang-{major}',
                      f'llvm-{major}-dev', f'lld-{major}'])


def require_tool(directory, name, major):
    path = directory / name
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f'LLVM {major}: missing executable {path}; provision with: '
                         f'{provision_toolchain(directory, major)}')
    return path
