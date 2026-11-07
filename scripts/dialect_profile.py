"""Explicit publication differences shared by the dialect checker components."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import StrEnum

LOWERING = {'BD-B-ISA4': 'K1', 'BD-B-ISA1': 'K3', 'BD-B-ISA12': 'K2', 'BD-B-ISA7': 'K5'}


class IsaVersion(StrEnum):
    LEGACY = '0.8'
    CURRENT = '0.9'


@dataclass(frozen=True)
class Publication:
    isa: IsaVersion
    spec_name: str

    @property
    def object_header(self):
        return 'bennett-object ' + ' '.join(f'{key}={self.isa}' for key in
                                          ('isa', 'object', 'launch', 'sched', 'cert', 'coverage', 'target'))

    def signature(self, signature):
        if self.isa is IsaVersion.CURRENT and signature['kind'] == 'lproc':
            return dict(signature, args=[], mem=[], tokens=[])
        return signature

    def verdict(self, verdict):
        return 'accept' if self.isa is IsaVersion.CURRENT and verdict.startswith('blocked:') else verdict

    def classify(self, verdict, info):
        if self.isa is IsaVersion.CURRENT:
            rows = [(LOWERING[code], reason) for code, reason in info.blockers]
            if info.reversible:
                for function in info.funcs():
                    if function.name in info.reversible and any(
                            marker in ('qalloc', 'qborrow', 'qfree')
                            for _, _, marker in info.marker_calls(function)):
                        rows.append(('K2', '§7.5(b) ledger frames in R: @' + function.name))
            info.lowerings = rows
            info.blockers = []
        return self.verdict(verdict), info


ISA08 = Publication(IsaVersion.LEGACY, 'Bennett-Dialect-Spec.md')
ISA09 = Publication(IsaVersion.CURRENT, 'Bennett-Dialect-Spec-0.3-draft.md')
_CURRENT = ContextVar('dialect_publication', default=ISA08)


def profile():
    return _CURRENT.get()


@contextmanager
def using_profile(publication):
    token = _CURRENT.set(publication)
    try:
        yield publication
    finally:
        _CURRENT.reset(token)
