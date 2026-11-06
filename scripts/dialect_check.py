#!/usr/bin/env python3
"""Public checker API composed from IR, analysis, rewriting and execution modules."""
import json
import sys
from dialect_pins import sibling
from dialect_ir import (
    ABI_WITH_ALIGN, ADJ, ATTR_TOKEN, BINOPS, B_DEFAULT, CCS, DECLS_TEXT, ENV_OP, FBINOPS, FMF, FORBIDDEN_LIE, FP_TYPES, Fail, Func, GATE1, GATE2, HANDLE_OPS, HEADER, HEAP_FNS, INT_CAND_OPS, INT_FLAGS, ISA_SPEC, Instr, LEG, LINKAGE, MAJORS, MARKERS, MARKERS_SHORT, Module, N4_FN, N4_PARAM, NORTH_STAR, OPCODES, PARAM_ATTR_WORDS, PERMITTED_FN, PERMITTED_PARAM, PERMITTED_RET, REGION_OPS, ROOT, Reject, SPEC, SPEC_PATH, TOOLCHAINS, UNSUPPORTED_FP, VISIBILITY, attr_name, attr_tokens, extract_blocks, fnstr, is_marker, marker_list, match_close, mname, parse_call, parse_type, split_top, strip_param_attrs, talign, tsize, tstr
)
from dialect_analysis import (
    Analysis, const_global_base, fn_consts_at, gep_offset, int_candidates, region_type_ok, store_parts, strip_flags, typed_val
)
from dialect_rewrite import (
    fault_replace, n7, normalise, print_module, ren, replace_uses, strip_attr_seq, strip_n4, strip_n4_header, validate
)
from dialect_execution import (
    adjoint, apply_gate, build_and_trace, check_markers, check_xrefs, classify, collapse, event_str, extract_function, headings, isa_anchor, lift, parse_amp, ref_hash, run, run_ref, simulate, toolchains, trace_to_events, validate_device, verify_all, verify_inplace, with_decls
)

def main(argv=None):
    # Make the parser module shared when invoked as a script or imported by tests.
    sys.modules.setdefault("dialect_check", sys.modules[__name__])
    from dialect_check_v02 import main as preflight
    return preflight(argv)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as error:
        print("FAIL:", error)
        sys.exit(1)

