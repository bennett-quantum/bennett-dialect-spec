// LLVM 18 pass plugin for the rung-4 SQLite spike.  Two module passes:
//
//   bennett-inventory   writes one JSON object per line describing every
//                       function and global of the module (facts only; the
//                       closure, SCCs and tables are computed by
//                       scripts/inventory.py).  Output: -bennett-out=<path>.
//
//   bennett-prof        instruments every defined function for the dynamic
//                       profile: a call per basic block (block id), per
//                       function entry/return, per load/store/atomic and per
//                       memcpy/memmove/memset intrinsic.  Writes the static
//                       tables (blocks, memory sites, functions) to
//                       -bennett-out=<path> and emits constant arrays the
//                       runtime (prof_rt.c) reads.
//
// Build: scripts/profile.sh (clang++ -shared against /usr/lib/llvm-18).
#include "llvm/IR/Constants.h"
#include "llvm/IR/DataLayout.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/InlineAsm.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/JSON.h"
#include "llvm/Support/raw_ostream.h"
#include <map>
#include <string>
#include <vector>

using namespace llvm;

static cl::opt<std::string> OutPath("bennett-out", cl::desc("output path"), cl::init(""));

namespace {

std::string typeStr(Type *T) {
  std::string S;
  raw_string_ostream OS(S);
  T->print(OS);
  return OS.str();
}

// Floating-point classification of an instruction: "<op>.<type>" or "".
std::string fpKey(Instruction &I) {
  auto isFP = [](Type *T) { return T->isFPOrFPVectorTy(); };
  Type *RT = I.getType();
  std::string op = I.getOpcodeName();
  if (auto *C = dyn_cast<CallBase>(&I)) {
    if (Function *F = C->getCalledFunction())
      if (F->isIntrinsic()) {
        bool any = isFP(RT);
        for (auto &A : C->args()) any |= isFP(A->getType());
        if (any) return F->getName().str();
      }
    return "";
  }
  if (isa<LoadInst>(I) || isa<StoreInst>(I) || isa<PHINode>(I) || isa<SelectInst>(I) ||
      isa<BitCastInst>(I) || isa<ExtractValueInst>(I) || isa<InsertValueInst>(I) ||
      isa<ExtractElementInst>(I) || isa<InsertElementInst>(I) || isa<ShuffleVectorInst>(I)) {
    // data movement of FP values: bit-exact, no soft-float needed; reported apart.
    Type *T = RT;
    if (auto *S = dyn_cast<StoreInst>(&I)) T = S->getValueOperand()->getType();
    if (isa<BitCastInst>(I) && !isFP(T)) T = I.getOperand(0)->getType();
    if (isFP(T)) return std::string("move:") + op + "." + typeStr(T);
    return "";
  }
  bool any = isFP(RT);
  for (auto &U : I.operands()) any |= isFP(U->getType());
  if (!any) return "";
  Type *T = isFP(RT) ? RT : I.getOperand(0)->getType();
  if (auto *FC = dyn_cast<FCmpInst>(&I)) return std::string("fcmp.") + typeStr(T);
  if (isa<CastInst>(I)) return op + "." + typeStr(I.getOperand(0)->getType()) + "->" + typeStr(RT);
  return op + "." + typeStr(T);
}

bool hasVector(Instruction &I) {
  if (I.getType()->isVectorTy()) return true;
  for (auto &U : I.operands())
    if (U->getType()->isVectorTy()) return true;
  return false;
}

// ---------------------------------------------------------------- inventory
struct InventoryPass : PassInfoMixin<InventoryPass> {
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
    std::error_code EC;
    raw_fd_ostream OS(OutPath, EC);
    if (EC) report_fatal_error("cannot open -bennett-out");
    const DataLayout &DL = M.getDataLayout();

    for (GlobalVariable &G : M.globals()) {
      json::Object O;
      O["kind"] = "global";
      O["name"] = G.getName().str();
      O["constant"] = G.isConstant();
      O["decl"] = G.isDeclaration();
      O["size"] = G.isDeclaration() ? 0 : (int64_t)DL.getTypeAllocSize(G.getValueType());
      bool zero = G.hasInitializer() && G.getInitializer()->isNullValue();
      O["zeroinit"] = zero;
      // functions whose address appears in the initializer
      json::Array Fns;
      if (G.hasInitializer()) {
        SmallVector<const Constant *, 16> Work{G.getInitializer()};
        SmallPtrSet<const Constant *, 32> Seen;
        while (!Work.empty()) {
          const Constant *C = Work.pop_back_val();
          if (!Seen.insert(C).second) continue;
          if (auto *F = dyn_cast<Function>(C)) { Fns.push_back(F->getName().str()); continue; }
          if (isa<GlobalValue>(C)) continue;
          for (auto &Op : C->operands())
            if (auto *CC = dyn_cast<Constant>(Op)) Work.push_back(CC);
        }
      }
      O["fn_refs"] = std::move(Fns);
      OS << json::Value(std::move(O)) << "\n";
    }

    for (Function &F : M) {
      json::Object O;
      O["kind"] = "function";
      O["name"] = F.getName().str();
      O["decl"] = F.isDeclaration();
      O["intrinsic"] = F.isIntrinsic();
      O["vararg"] = F.isVarArg();
      O["fty"] = typeStr(F.getFunctionType());
      O["linkage"] = (int64_t)F.getLinkage();
      O["address_taken"] = F.hasAddressTaken(nullptr, /*IgnoreCallbackUses*/ false,
                                              /*IgnoreAssumeLikeCalls*/ true,
                                              /*IgnoreLLVMUsed*/ true);
      if (F.isDeclaration()) { OS << json::Value(std::move(O)) << "\n"; continue; }

      std::map<std::string, int64_t> ops, calls, intr, fp, icalls, globals, loadw, storew, vec;
      int64_t nbb = 0, ninst = 0, mprime = F.arg_size(), allocaBytes = 0, dynAlloca = 0;
      int64_t valueBits = 0, maxValueBits = 0, maxPhis = 0, maxPhiBits = 0, maxCallArgs = 0, maxCallArgBits = 0;
      auto bitsOf = [&](Type *T) -> int64_t {
        if (T->isPointerTy()) return DL.getPointerSizeInBits();
        if (T->isVoidTy() || T->isLabelTy() || T->isMetadataTy() || T->isTokenTy()) return 0;
        return (int64_t)DL.getTypeSizeInBits(T).getFixedValue();
      };
      for (Argument &A : F.args()) { valueBits += bitsOf(A.getType()); }
      int64_t vaStart = 0, vaArg = 0, asmCalls = 0, maxSwitch = 0, switches = 0, nAtomic = 0,
              nVolatile = 0, nVarargCalls = 0, nIndirectBr = 0, nUnreachable = 0, nInvoke = 0;
      json::Array vecEx, asmEx;
      for (BasicBlock &BB : F) {
        nbb++;
        int64_t phis = 0, phiBits = 0;
        for (PHINode &P : BB.phis()) { phis++; phiBits += bitsOf(P.getType()); }
        maxPhis = std::max(maxPhis, phis);
        maxPhiBits = std::max(maxPhiBits, phiBits);
        for (Instruction &I : BB) {
          if (isa<DbgInfoIntrinsic>(I)) continue;
          ninst++;
          if (!I.getType()->isVoidTy()) {
            mprime++;
            int64_t b = bitsOf(I.getType());
            valueBits += b;
            maxValueBits = std::max(maxValueBits, b);
          }
          if (auto *CB = dyn_cast<CallBase>(&I); CB && !isa<IntrinsicInst>(I)) {
            int64_t ab = 0;
            for (auto &A : CB->args()) ab += bitsOf(A->getType());
            maxCallArgs = std::max<int64_t>(maxCallArgs, CB->arg_size());
            maxCallArgBits = std::max(maxCallArgBits, ab);
          }
          ops[I.getOpcodeName()]++;
          std::string k = fpKey(I);
          if (!k.empty()) fp[k]++;
          if (hasVector(I)) {
            vec[I.getOpcodeName()]++;
            if (vecEx.size() < 3) {
              std::string S; raw_string_ostream SO(S); I.print(SO); vecEx.push_back(SO.str());
            }
          }
          for (auto &U : I.operands()) {
            Value *V = U.get()->stripPointerCasts();
            if (auto *GV = dyn_cast<GlobalVariable>(V)) globals[GV->getName().str()]++;
            else if (auto *CE = dyn_cast<ConstantExpr>(U.get()))
              for (auto &U2 : CE->operands())
                if (auto *GV2 = dyn_cast<GlobalVariable>(U2.get()->stripPointerCasts()))
                  globals[GV2->getName().str()]++;
          }
          if (auto *L = dyn_cast<LoadInst>(&I)) {
            loadw[std::to_string(DL.getTypeStoreSize(L->getType()))]++;
            if (L->isAtomic()) nAtomic++;
            if (L->isVolatile()) nVolatile++;
          } else if (auto *S = dyn_cast<StoreInst>(&I)) {
            storew[std::to_string(DL.getTypeStoreSize(S->getValueOperand()->getType()))]++;
            if (S->isAtomic()) nAtomic++;
            if (S->isVolatile()) nVolatile++;
          } else if (isa<AtomicRMWInst>(I) || isa<AtomicCmpXchgInst>(I) || isa<FenceInst>(I)) {
            nAtomic++;
          } else if (auto *A = dyn_cast<AllocaInst>(&I)) {
            auto Sz = A->getAllocationSize(DL);
            if (Sz && A->isStaticAlloca()) allocaBytes += (int64_t)Sz->getFixedValue();
            else dynAlloca++;
          } else if (isa<VAArgInst>(I)) {
            vaArg++;
          } else if (auto *SW = dyn_cast<SwitchInst>(&I)) {
            switches++;
            maxSwitch = std::max<int64_t>(maxSwitch, SW->getNumCases());
          } else if (isa<IndirectBrInst>(I)) {
            nIndirectBr++;
          } else if (isa<UnreachableInst>(I)) {
            nUnreachable++;
          }
          if (isa<InvokeInst>(I)) nInvoke++;
          if (auto *C = dyn_cast<CallBase>(&I)) {
            if (C->isInlineAsm()) {
              asmCalls++;
              if (asmEx.size() < 3)
                asmEx.push_back(cast<InlineAsm>(C->getCalledOperand())->getAsmString());
              continue;
            }
            if (C->getFunctionType()->isVarArg()) nVarargCalls++;
            Function *Callee = C->getCalledFunction();
            if (Callee) {
              if (Callee->isIntrinsic()) {
                intr[Callee->getName().str()]++;
                if (Callee->getIntrinsicID() == Intrinsic::vastart) vaStart++;
              } else {
                calls[Callee->getName().str()]++;
              }
            } else {
              icalls[typeStr(C->getFunctionType())]++;
            }
          }
        }
      }
      auto toObj = [](std::map<std::string, int64_t> &m) {
        json::Object o;
        for (auto &kv : m) o[kv.first] = kv.second;
        return o;
      };
      O["nbb"] = nbb;
      O["ninst"] = ninst;
      O["mprime"] = mprime;
      O["value_bits"] = valueBits;
      O["max_value_bits"] = maxValueBits;
      O["max_phis_block"] = maxPhis;
      O["max_phi_bits_block"] = maxPhiBits;
      O["max_call_args"] = maxCallArgs;
      O["max_call_arg_bits"] = maxCallArgBits;
      O["ops"] = toObj(ops);
      O["calls"] = toObj(calls);
      O["icalls"] = toObj(icalls);
      O["intrinsics"] = toObj(intr);
      O["fp"] = toObj(fp);
      O["vector"] = toObj(vec);
      O["vector_examples"] = std::move(vecEx);
      O["globals"] = toObj(globals);
      O["load_bytes"] = toObj(loadw);
      O["store_bytes"] = toObj(storew);
      O["alloca_static_bytes"] = allocaBytes;
      O["alloca_dynamic"] = dynAlloca;
      O["va_start"] = vaStart;
      O["va_arg"] = vaArg;
      O["vararg_calls"] = nVarargCalls;
      O["inline_asm"] = asmCalls;
      O["inline_asm_examples"] = std::move(asmEx);
      O["atomics"] = nAtomic;
      O["volatile"] = nVolatile;
      O["switches"] = switches;
      O["max_switch_cases"] = maxSwitch;
      O["indirectbr"] = nIndirectBr;
      O["unreachable"] = nUnreachable;
      O["invoke"] = nInvoke;
      OS << json::Value(std::move(O)) << "\n";
    }
    return PreservedAnalyses::all();
  }
};

// ------------------------------------------------------------ instrumentation
// Per-block category counts written to the table; scripts/analyze.py maps
// them to ISA-row estimates.
enum Cat { C_LOAD, C_STORE, C_GEP, C_PHI, C_BR, C_SWITCH_CASES, C_CALL, C_ICALL, C_INTR, C_MEMX,
           C_FP, C_ALLOCA, C_RET, C_SELECT, C_CMP, C_CAST, C_ARITH, C_MULDIV, C_OTHER, C_NOP, C_NCAT };
static const char *CatName[C_NCAT] = {"load", "store", "gep", "phi", "br", "switch_cases", "call",
                                      "icall", "intrinsic", "memx", "fp", "alloca", "ret", "select",
                                      "cmp", "cast", "arith", "muldiv", "other", "nop"};

struct ProfPass : PassInfoMixin<ProfPass> {
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
    std::error_code EC;
    raw_fd_ostream OS(OutPath, EC);
    if (EC) report_fatal_error("cannot open -bennett-out");
    LLVMContext &Ctx = M.getContext();
    const DataLayout &DL = M.getDataLayout();
    Type *I32 = Type::getInt32Ty(Ctx), *I64 = Type::getInt64Ty(Ctx), *VoidT = Type::getVoidTy(Ctx);
    PointerType *Ptr = PointerType::getUnqual(Ctx);
    FunctionCallee FBB = M.getOrInsertFunction("__prof_bb", VoidT, I32);
    FunctionCallee FEnter = M.getOrInsertFunction("__prof_enter", VoidT, I32);
    FunctionCallee FExit = M.getOrInsertFunction("__prof_exit", VoidT, I32);
    FunctionCallee FLd = M.getOrInsertFunction("__prof_ld", VoidT, Ptr, I32, I32);
    FunctionCallee FSt = M.getOrInsertFunction("__prof_st", VoidT, Ptr, I32, I32, I64);
    FunctionCallee FMemx = M.getOrInsertFunction("__prof_memx", VoidT, Ptr, Ptr, I64, I32, I32);
    FunctionCallee FDynA = M.getOrInsertFunction("__prof_alloca", VoidT, I64);
    FunctionCallee FVal = M.getOrInsertFunction("__prof_val", VoidT, I32, I64);
    uint32_t valId = 0;
    std::string valTab = "#val\tvid\tbid\tcat\n";
    raw_string_ostream VT(valTab);

    std::vector<Function *> Fns;
    for (Function &F : M)
      if (!F.isDeclaration() && !F.getName().starts_with("__prof")) Fns.push_back(&F);

    uint32_t bbId = 0, memId = 0, fnId = 0;
    std::vector<Constant *> bbNinst, fnMprime, fnAlloca;
    OS << "#functions\tfid\tname\tmprime\talloca_bytes\tnbb\n";
    std::string blocksTab = "#blocks\tbid\tfid\tninst";
    for (int c = 0; c < C_NCAT; c++) blocksTab += std::string("\t") + CatName[c];
    blocksTab += "\n";
    std::string memTab = "#mem\tmid\tbid\tkind\tsize\n";
    raw_string_ostream BT(blocksTab), MT(memTab);

    for (Function *F : Fns) {
      uint32_t fid = fnId++;
      int64_t mprime = F->arg_size(), allocaBytes = 0;
      std::vector<std::pair<BasicBlock *, uint32_t>> blocks;
      for (BasicBlock &BB : *F) blocks.push_back({&BB, bbId++});
      // collect instructions first (we insert while iterating otherwise)
      for (auto &[BB, bid] : blocks) {
        int64_t cnt[C_NCAT] = {0};
        int64_t ninst = 0;
        std::vector<Instruction *> Insts;
        for (Instruction &I : *BB) {
          if (isa<DbgInfoIntrinsic>(I)) continue;
          Insts.push_back(&I);
        }
        for (Instruction *I : Insts) {
          ninst++;
          if (!I->getType()->isVoidTy()) mprime++;
          Cat c = C_OTHER;
          if (isa<LoadInst>(I)) c = C_LOAD;
          else if (isa<StoreInst>(I)) c = C_STORE;
          else if (isa<AtomicRMWInst>(I) || isa<AtomicCmpXchgInst>(I)) c = C_STORE;
          else if (isa<GetElementPtrInst>(I)) c = C_GEP;
          else if (isa<PHINode>(I)) c = C_PHI;
          else if (isa<BranchInst>(I)) c = C_BR;
          else if (auto *SW = dyn_cast<SwitchInst>(I)) { c = C_SWITCH_CASES; cnt[c] += SW->getNumCases(); }
          else if (isa<ReturnInst>(I)) c = C_RET;
          else if (isa<SelectInst>(I)) c = C_SELECT;
          else if (isa<ICmpInst>(I)) c = C_CMP;
          else if (isa<AllocaInst>(I)) c = C_ALLOCA;
          else if (auto *II = dyn_cast<IntrinsicInst>(I);
                   II && (II->isAssumeLikeIntrinsic() || II->getIntrinsicID() == Intrinsic::lifetime_start ||
                          II->getIntrinsicID() == Intrinsic::lifetime_end))
            c = C_NOP;
          else if (!fpKey(*I).empty() && fpKey(*I).rfind("move:", 0) != 0) c = C_FP;
          else if (isa<CastInst>(I)) c = C_CAST;
          else if (auto *C = dyn_cast<CallBase>(I)) {
            Function *Cal = C->getCalledFunction();
            if (isa<MemIntrinsic>(I)) c = C_MEMX;
            else if (Cal && Cal->isIntrinsic()) c = C_INTR;
            else if (Cal) c = C_CALL;
            else c = C_ICALL;
          } else if (auto *BO = dyn_cast<BinaryOperator>(I)) {
            auto op = BO->getOpcode();
            c = (op == Instruction::Mul || op == Instruction::UDiv || op == Instruction::SDiv ||
                 op == Instruction::URem || op == Instruction::SRem) ? C_MULDIV : C_ARITH;
          }
          if (c != C_SWITCH_CASES) cnt[c]++;

          // value tracking: integer/pointer results up to 64 bits
          Type *RT = I->getType();
          if ((RT->isIntegerTy() && RT->getIntegerBitWidth() <= 64) || RT->isPointerTy()) {
            if (!I->isTerminator()) {
              Instruction *At = isa<PHINode>(I) ? &*BB->getFirstInsertionPt() : I->getNextNode();
              IRBuilder<> BV(At);
              Value *Bits = RT->isPointerTy() ? BV.CreatePtrToInt(I, I64) : BV.CreateZExt(I, I64);
              BV.CreateCall(FVal, {BV.getInt32(valId), Bits});
              VT << "V\t" << valId << "\t" << bid << "\t" << CatName[c] << "\n";
              valId++;
            }
          }

          // instrumentation of memory operations
          IRBuilder<> B(I);
          if (auto *L = dyn_cast<LoadInst>(I)) {
            uint32_t sz = DL.getTypeStoreSize(L->getType());
            B.CreateCall(FLd, {L->getPointerOperand(), B.getInt32(sz), B.getInt32(memId)});
            MT << "M\t" << memId << "\t" << bid << "\tload\t" << sz << "\n";
            memId++;
          } else if (auto *S = dyn_cast<StoreInst>(I)) {
            Value *V = S->getValueOperand();
            uint32_t sz = DL.getTypeStoreSize(V->getType());
            Value *Bits = ConstantInt::get(I64, 0);
            Type *VT = V->getType();
            if (VT->isIntegerTy() && VT->getIntegerBitWidth() <= 64) Bits = B.CreateZExt(V, I64);
            else if (VT->isPointerTy()) Bits = B.CreatePtrToInt(V, I64);
            else if (VT->isDoubleTy()) Bits = B.CreateBitCast(V, I64);
            else if (VT->isFloatTy()) Bits = B.CreateZExt(B.CreateBitCast(V, I32), I64);
            B.CreateCall(FSt, {S->getPointerOperand(), B.getInt32(sz), B.getInt32(memId), Bits});
            MT << "M\t" << memId << "\t" << bid << "\tstore\t" << sz << "\n";
            memId++;
          } else if (auto *A = dyn_cast<AtomicRMWInst>(I)) {
            uint32_t sz = DL.getTypeStoreSize(A->getValOperand()->getType());
            B.CreateCall(FSt, {A->getPointerOperand(), B.getInt32(sz), B.getInt32(memId),
                               ConstantInt::get(I64, 0)});
            MT << "M\t" << memId << "\t" << bid << "\tatomicrmw\t" << sz << "\n";
            memId++;
          } else if (auto *X = dyn_cast<AtomicCmpXchgInst>(I)) {
            uint32_t sz = DL.getTypeStoreSize(X->getNewValOperand()->getType());
            B.CreateCall(FSt, {X->getPointerOperand(), B.getInt32(sz), B.getInt32(memId),
                               ConstantInt::get(I64, 0)});
            MT << "M\t" << memId << "\t" << bid << "\tcmpxchg\t" << sz << "\n";
            memId++;
          } else if (auto *MI = dyn_cast<MemIntrinsic>(I)) {
            Value *Src = ConstantPointerNull::get(Ptr);
            int kind = 0;
            if (auto *MT2 = dyn_cast<MemTransferInst>(MI)) { Src = MT2->getRawSource(); kind = isa<MemMoveInst>(MI) ? 2 : 1; }
            Value *Len = B.CreateZExtOrTrunc(MI->getLength(), I64);
            B.CreateCall(FMemx, {MI->getRawDest(), Src, Len, B.getInt32(kind), B.getInt32(memId)});
            MT << "M\t" << memId << "\t" << bid << "\t" << (kind == 0 ? "memset" : kind == 1 ? "memcpy" : "memmove") << "\t0\n";
            memId++;
          } else if (auto *AI = dyn_cast<AllocaInst>(I)) {
            auto Sz = AI->getAllocationSize(DL);
            if (Sz && AI->isStaticAlloca()) allocaBytes += (int64_t)Sz->getFixedValue();
            else {
              IRBuilder<> B2(AI->getNextNode());
              Value *N = B2.CreateZExtOrTrunc(AI->getArraySize(), I64);
              Value *Bytes = B2.CreateMul(N, ConstantInt::get(I64, DL.getTypeAllocSize(AI->getAllocatedType())));
              B2.CreateCall(FDynA, {Bytes});
            }
          } else if (auto *R = dyn_cast<ReturnInst>(I)) {
            B.CreateCall(FExit, {B.getInt32(fid)});
          }
        }
        BT << "B\t" << bid << "\t" << fid << "\t" << ninst;
        for (int c = 0; c < C_NCAT; c++) BT << "\t" << cnt[c];
        BT << "\n";
        bbNinst.push_back(ConstantInt::get(I32, ninst));
        IRBuilder<> B(&*BB->getFirstInsertionPt());
        B.CreateCall(FBB, {B.getInt32(bid)});
        if (BB == &F->getEntryBlock()) B.CreateCall(FEnter, {B.getInt32(fid)});
      }
      OS << "F\t" << fid << "\t" << F->getName() << "\t" << mprime << "\t" << allocaBytes << "\t"
         << blocks.size() << "\n";
      fnMprime.push_back(ConstantInt::get(I32, mprime));
      fnAlloca.push_back(ConstantInt::get(I32, allocaBytes));
    }
    OS << BT.str() << MT.str() << VT.str();

    auto emitArr = [&](const char *name, std::vector<Constant *> &v) {
      if (v.empty()) v.push_back(ConstantInt::get(I32, 0));
      ArrayType *AT = ArrayType::get(I32, v.size());
      new GlobalVariable(M, AT, true, GlobalValue::ExternalLinkage, ConstantArray::get(AT, v), name);
    };
    emitArr("__prof_bb_ninst", bbNinst);
    emitArr("__prof_fn_mprime", fnMprime);
    emitArr("__prof_fn_alloca", fnAlloca);
    auto emitScalar = [&](const char *name, uint32_t v) {
      new GlobalVariable(M, I32, true, GlobalValue::ExternalLinkage, ConstantInt::get(I32, v), name);
    };
    emitScalar("__prof_nblocks", bbId);
    emitScalar("__prof_nmem", memId);
    emitScalar("__prof_nfuncs", fnId);
    emitScalar("__prof_nvals", valId);
    return PreservedAnalyses::none();
  }
};

} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "BennettSpike", "0.1", [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM, ArrayRef<PassBuilder::PipelineElement>) {
                  if (Name == "bennett-inventory") { MPM.addPass(InventoryPass()); return true; }
                  if (Name == "bennett-prof") { MPM.addPass(ProfPass()); return true; }
                  return false;
                });
          }};
}
