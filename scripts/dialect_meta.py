"""Mechanical spec metadata checks: budget schema, cross-references, rule coverage, asm."""
import fnmatch
import json
from pathlib import Path
import re
import dialect_check as d
from dialect_check_v02 import equal


def budget_table(runner,block):
    ident=block['attrs']['budget-table'];obj=json.loads(block['body'])
    equal(ident,'§9.2 canonical JSON',json.dumps(obj,sort_keys=True,separators=(',',':')),block['body'].strip())
    equal(ident,'§9.2 version','0.2',obj['version'])
    allowed={'steps','heap','stack','depth','sstack'}
    for row in [obj['defaults'],*obj['entries']]:
        for k,v in row.items():
            if k in allowed and (not isinstance(v,str) or not re.fullmatch(r'\d+',v)):raise d.Fail(f'§9.2 expected decimal string for {k}; actual={v!r}')
            if k not in allowed|{'identity','region_key','symbol'}:raise d.Fail('§9.2 unexpected field '+k)
    for e in obj['entries']:
        equal(ident,'§9.2 selector count',1,sum(k in e for k in ('identity','region_key','symbol')))
    src=runner.block('lift',ident);name=src['attrs']['region'].lstrip('@')
    resolved=resolve_budget(obj,name)
    expected={k:int(v) for e in obj['entries'] if fnmatch.fnmatchcase(name,e.get('symbol','')) for k,v in e.items() if k in allowed}
    for k,v in expected.items():equal(ident,'§9.2 '+k,v,resolved[k])


def resolve_budget(table,symbol,identity='',region_key=''):
    defaults={'steps':1048576,'heap':1048576,'stack':65536,'depth':256,'sstack':65536}
    defaults.update({k:int(v) for k,v in table.get('defaults',{}).items()})
    for component in defaults:
        for selector,actual in (('identity',identity),('region_key',region_key),('symbol',symbol)):
            candidates=[e for e in table['entries'] if component in e and selector in e and
                        (fnmatch.fnmatchcase(actual,e[selector]) if selector=='symbol' else e[selector]==actual)]
            if candidates:defaults[component]=int(candidates[0][component]);break
    return defaults


def xrefs(text):
    own=d.headings(d.SPEC_PATH);isa=d.headings(d.ISA_SPEC);ns=d.headings(d.NORTH_STAR)
    questions=d.NORTH_STAR.read_text().split('## 9.',1)[1].split('## 10.',1)[0]
    ns.update('9.'+n for n in re.findall(r'^(\d+)\. ',questions,re.M))
    previous_doc=None;end=-1;results=[]
    for m in re.finditer(r'§(\d+(?:\.\d+)*)',text):
        before=text[max(0,m.start()-60):m.start()];between=text[end:m.start()]
        if previous_doc and re.fullmatch(r'\s*(?:[,–-]|and|or|to)\s*',between):doc=previous_doc
        elif re.search(r'ISA\s*$',before):doc='ISA'
        elif re.search(r'(?:NS|[Nn]orth [Ss]tar)\s*$',before):doc='NS'
        elif re.search(r'(?:findings|survey|triage|summary|plan|outline|audit)\s*$',before):doc='external'
        elif re.search(r'0\.1\s*$',before):doc='historical'
        else:doc='dialect'
        previous_doc=doc;end=m.end()
        if doc in ('external','historical'):continue
        results.append((text.count('\n',0,m.start())+1,doc,m[1],m[1] in {'dialect':own,'ISA':isa,'NS':ns}[doc]))
    return results


def expand_rules(text):
    rules=set(re.findall(r'\b(?:N|V|PT|TDL-|S|BLK-)\d+\b',text))
    for prefix,a,b in re.findall(r'\b(N|V|PT|TDL-|S|BLK-)(\d+)[–-](?:(?:N|V|PT|TDL-|S|BLK-))?(\d+)\b',text):
        rules.update(prefix+str(i) for i in range(int(a),int(b)+1))
    return rules


def coverage(runner):
    text=runner.spec;idx=text.split('## Appendix B.',1)[1].split('## Appendix C.',1)[0]
    covered=set();evidence={}
    # Index claims are resolved against actual accepted example tags, not names alone.
    for line in idx.splitlines():
        if not line.startswith('| `'):continue
        columns=line.split('|');names=columns[1];rules=expand_rules(columns[2]);patterns=re.findall(r'`([^`]+)`',names)
        matches=[]
        for b in runner.blocks:
            a=b['attrs'];ident=next((a[k] for k in ('example','normalise-in','lift','semantics','tdl') if k in a),'')
            if any(fnmatch.fnmatchcase(ident,p) for p in patterns) and (a.get('verdict','accept')=='accept'):
                matches.append(ident)
        if matches:
            covered|=rules
            for rule in rules:evidence.setdefault(rule,[]).extend(matches)
    # All accepted modules traverse S1–S9. Retired N anchors inherit replacement rules.
    for n in range(1,10):covered.add('S'+str(n))
    for old,replacement in ((13,26),(17,32),(18,28),(19,32),(20,24)):
        if 'N'+str(replacement) in covered:covered.add('N'+str(old))
    anchors=set()
    for section in (text.split('### 12.2 The rules',1)[1].split('### 12.3',1)[0],
                    text.split('### 12.4 The residual-poison validator',1)[1].split('### 12.5',1)[0],
                    text.split('### 5.2 Rules',1)[1].split('### 5.3',1)[0]):
        for line in section.splitlines():
            m=re.match(r'\| ((?:N|V|PT)\d+) \|',line)
            if m:anchors.add(m[1])
    anchors|={'TDL-'+str(i) for i in range(1,13)}|{'S'+str(i) for i in range(1,10)}
    results={rule:rule in covered for rule in sorted(anchors)}
    # §22.1 rejection codes must have a negative example; §25.1 blocker codes likewise.
    diagnostics=text.split('### 22.1 Compile-time rejections',1)[1].split('**Deleted**',1)[0]
    verdicts={b['attrs'].get('verdict') for b in runner.blocks}
    for code in re.findall(r'\| `(BD-E-[A-Z-]+)`',diagnostics):results[code]='reject:'+code in verdicts
    for code in re.findall(r'\| \*\*BLK-\d+\*\*.*?`(BD-B-ISA\d+)`',text):results[code]='blocked:'+code in verdicts
    # Explicit coverage obligations outside numbered mechanism rules.
    lifted='\n'.join(b['attrs'].get('desc','') for b in runner.blocks if 'lift' in b['attrs'])
    for kind in ('IN','ARG','MEM_IN','OUT'):results['binding:'+kind]=bool(re.search(r'\b'+kind+r'\(',lifted))
    for model in ('ENTROPY','BLOCK','CLOCK','CONSOLE'):results['device:'+model]=model+'(' in lifted
    bodies='\n'.join(b['body'] for b in runner.blocks if 'lift' in b['attrs'])
    results['§8.5 entry-state transfer']='__bennett_rt_entry_replay' in bodies
    results['§14.9 indirectbr']='indirectbr ' in bodies
    for section in [f'19.{i}' for i in range(3,9)]+['20']:
        results['§'+section]=False  # No such example tag in Appendix B; b-dialect-spec-gvr.
    return results,evidence


def asm_rows(text):
    expected={a:[] for a in ('x86-64','aarch64','riscv64')}
    def add(arch,asm,constraints,cls,replacement,section,match='exact'):
        expected[arch].append({'asm':asm,'constraints':constraints,'class':cls,'replacement':replacement,'section':section,'match':match})
    # Read the syscall ABI table rather than duplicating its argument-register lists.
    section=text.split('### 15.5 Required rows for 0.2',1)[1].split('```llvm',1)[0]
    arch_names={'x86-64':'x86-64','AArch64':'aarch64','RISC-V64':'riscv64'}
    for ln in section.splitlines():
        if not ln.startswith('| ') or not any('| '+n+' |' in ln for n in arch_names):continue
        cols=ln.split('|');arch=arch_names[cols[1].strip()];asm=re.findall(r'`([^`]+)`',cols[2])[0]
        pieces=re.findall(r'`([^`]+)`',cols[3]);head,registers,clobbers=pieces
        for k in range(7):
            constraint=','.join([head,*registers.split(',')[:k],clobbers]);args=['i64 nr']+['i64 a'+str(i) for i in range(1,k+1)]+['i64 0']*(6-k)
            add(arch,asm,constraint,'shimmed','call i64 @__bennett_rt_syscall('+', '.join(args)+')','15.5')
    for arch in expected:
        add(arch,'','* (without outputs)','lowered','deleted','15.2','pattern')
        add(arch,'nop','*','lowered','deleted','15.2','mnemonic')
    for arch,names in [('x86-64',['pause','llvm.x86.sse2.pause']),('aarch64',['yield','llvm.aarch64.hint']),('riscv64',['fence','fence rw,rw','fence.i'])]:
        for name in names:
            if name not in text:raise d.Fail('§15.2 missing published asm row '+name)
            add(arch,name,'*','lowered','deleted','15.2','mnemonic')
    for arch,names in [('x86-64',['rdtsc','llvm.x86.rdtsc']),('aarch64',['mrs $0, cntvct_el0']),('riscv64',['rdtime','rdcycle'])]:
        for name in names:add(arch,name,'={ax},={dx}' if name=='rdtsc' else '*','lowered','call i64 @__bennett_rt_cyclecounter()','15.2','exact' if name=='rdtsc' else 'pattern')
    for arch in expected:
        for name in ('llvm.readcyclecounter','llvm.readsteadycounter'):add(arch,name,'*','lowered','call i64 @__bennett_rt_cyclecounter()','15.2','intrinsic')
        add(arch,'*','*','trapped','F(8)','15.2','fallback')
    add('x86-64','cpuid','*','lowered','lookup declared CPU leaf table','15.2','mnemonic')
    platform={'csrr':'csr_read','csrw':'csr_write','csrs':'csr_set','csrc':'csr_clear','csrrwi':'csr_write','csrrsi':'csr_set','csrrci':'csr_clear','sfence.vma':'sfence_vma','wfi':'wfi','ecall':'sbi_call (kernel); trap path (user)','mret':'trap_return (machine)','sret':'trap_return (supervisor)'}
    for asm,repl in platform.items():add('riscv64',asm,'platform-spike inventory (§20.7)','shimmed','__bennett_rt_'+repl,'20.2','platform-pattern')
    return expected


def write_asm(text,directory):
    directory.mkdir(exist_ok=True)
    for arch,rows in asm_rows(text).items():
        output=['# Generated from dialect §15 and §20.2; section prevails.','version = "0.2"','architecture = '+json.dumps(arch)]
        for row in rows:
            output.append('\n[[rows]]')
            output += [k+' = '+json.dumps(v) for k,v in row.items()]
        (directory/(arch+'.toml')).write_text('\n'.join(output)+'\n')


def check_asm(runner):
    import tomllib
    for arch,rows in asm_rows(runner.spec).items():
        path=d.ROOT/'spec'/'asm'/(arch+'.toml')
        data=tomllib.loads(path.read_text());equal(arch,'§15.1 version','0.2',data['version'])
        equal(arch,'§15/§20.2 rows',rows,data['rows'])
