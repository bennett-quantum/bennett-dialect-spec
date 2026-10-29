#![crate_type = "lib"]
#![allow(non_camel_case_types)]
use core::ffi::c_void;

#[repr(C)] pub struct bq_opaque { _p: [u8; 0] }
pub type bq = *mut bq_opaque;
pub type bregion = extern "C" fn(*mut c_void);

extern "C" {
    fn __bennett_qalloc(cls: u64, n: u64) -> bq;
    fn __bennett_qborrow(cls: u64, n: u64) -> bq;
    fn __bennett_qfree(h: bq);
    fn __bennett_gate(op: u32, h: bq, i: u64);
    fn __bennett_gate2(op: u32, a: bq, i: u64, b: bq, j: u64);
    fn __bennett_rot(op: u32, h: bq, i: u64, theta: f64);
    fn __bennett_measure(h: bq, i: u64) -> bool;
    fn __bennett_qload(dst: bq, mem: bq, addr: bq);
    fn __bennett_qstore(mem: bq, addr: bq, val: bq);
    fn __bennett_ctrl(q: bq, qi: u64, f: bregion, budget: u64, env: *mut c_void);
    fn __bennett_adj(f: bregion, env: *mut c_void);
    fn __bennett_compute(f: bregion, usef: bregion, env: *mut c_void);
    fn __bennett_reversible(f: bregion, budget: u64, env: *mut c_void);
    fn __bennett_inplace(g: bregion, ginv: bregion, env: *mut c_void);
    fn __bennett_ctrl_v(q: bq, qi: u64, f: *mut c_void, budget: u64, ...);
}
// Same declarations again but with "C-unwind" ABI, to see nounwind vs not.
extern "C-unwind" {
    #[link_name = "__bennett_qfree"] fn qfree_unwind(h: bq);
    #[link_name = "__bennett_gate"] fn gate_unwind(op: u32, h: bq, i: u64);
}

#[repr(C)] pub struct Env { h: bq, i: u64, theta: f64 }

extern "C" fn body(p: *mut c_void) {
    unsafe {
        let e = &*(p as *mut Env);
        __bennett_rot(1, e.h, e.i, e.theta);
        __bennett_gate(2, e.h, e.i);
    }
}
// closure-to-fn-pointer: non-capturing closure coerces to Rust-ABI fn, so wrap in extern "C" via a generic trampoline.
extern "C" fn tramp<F: Fn(&mut Env)>(p: *mut c_void) {
    // F is zero-sized; conjure it
    let f: F = unsafe { core::mem::MaybeUninit::<F>::uninit().assume_init() };
    f(unsafe { &mut *(p as *mut Env) });
}
fn region_of<F: Fn(&mut Env)>(_f: F) -> bregion { assert!(core::mem::size_of::<F>() == 0); tramp::<F> }

struct Guard(bq);
impl Drop for Guard { fn drop(&mut self) { unsafe { __bennett_qfree(self.0) } } }

#[inline(never)] #[no_mangle]
pub extern "C" fn rt_may_unwind(x: u64) { if x == 77 { panic!("x") } }

#[no_mangle]
pub unsafe extern "C" fn case_entry(x: u64) -> u64 {
    let h = __bennett_qalloc(0, 4);
    __bennett_gate(1, h, 0);
    let theta = (x as f64) * 0.125;
    __bennett_rot(3, h, 1, theta);
    __bennett_gate2(4, h, 0, h, 1);
    let mut r = 0;
    if __bennett_measure(h, 0) { __bennett_gate(2, h, 2); r = 1; }
    let mut e = Env { h, i: 3, theta };
    __bennett_ctrl(h, 0, body, 8, &mut e as *mut Env as *mut c_void);
    // closure route
    let f = region_of(|e: &mut Env| { __bennett_gate(5, e.h, e.i) });
    __bennett_ctrl(h, 1, f, 8, &mut e as *mut Env as *mut c_void);
    let mut tab = [core::ptr::null_mut::<bq_opaque>(); 4];
    for k in 0..4 { tab[k] = __bennett_qalloc(0, 1); }
    __bennett_gate(1, tab[(x & 3) as usize], 0);
    __bennett_ctrl_v(h, 0, body as *mut c_void, 8, 1i32, 2.5f64, h);
    __bennett_adj(body, &mut e as *mut Env as *mut c_void);
    __bennett_compute(body, body, &mut e as *mut Env as *mut c_void);
    __bennett_reversible(body, 3, &mut e as *mut Env as *mut c_void);
    __bennett_inplace(body, body, &mut e as *mut Env as *mut c_void);
    {
        let g = Guard(__bennett_qborrow(0, 1));
        __bennett_qload(g.0, h, tab[0]);
        __bennett_qstore(h, tab[1], g.0);
        rt_may_unwind(x);   // unwinding edge -> Guard::drop calls qfree via cleanup
        gate_unwind(6, g.0, 0);
    }
    qfree_unwind(h);
    for k in 0..4 { __bennett_qfree(tab[k]); }
    __bennett_qfree(h);
    r
}
