"""Native differential adapters. Inputs/expectations are parsed from tagged text.
The compiler and executable supply observations; Python only compares them.
"""
import ast
import json
import re
import subprocess
from pathlib import Path
import dialect_check as d

SEEDS=d.ROOT/'spec'/'seeds'
PREFIX='#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\n'


def values(text):
    text=text.replace('all ones x 4',', '.join(['18446744073709551615']*4))
    return ast.literal_eval(text)


def cases(ident,text):
    """Return C driver, independent expected stdout records, module variants."""
    out=[];expected=[];decl='';variants=('input','output')
    if ident in ('n-shadow-stack','n-varargs','n-intrinsics','n-eh'):
        name={'n-shadow-stack':'a','n-varargs':'top','n-intrinsics':'k','n-eh':'eh'}[ident]
        ret='int64_t' if ident=='n-shadow-stack' else 'int32_t'
        count=2 if ident=='n-intrinsics' else 1
        decl=f'extern {ret} {name}('+','.join([ret]*count)+');\n'
        for args,want in re.findall(r'\b'+name+r'\(([-\d, ]+)\) = (-?\d+)',text):
            out.append(f'printf("%lld\\n", (long long){name}({args}));');expected.append(int(want))
        if ident=='n-shadow-stack':variants=('output',)
    elif ident=='n-vector':
        decl='extern int32_t v(const int32_t *,const int32_t *);\n'
        for j,(a,b,want) in enumerate(re.findall(r'v\((\[[^]]+\]), (\[[^]]+\])\) = (-?\d+)',text)):
            aa,bb=values(a),values(b)
            out.append('int32_t a%d[]={%s},b%d[]={%s};'%(j,','.join(map(str,aa)),j,','.join(map(str,bb))))
            out.append(f'printf("%d\\n", v(a{j},b{j}));');expected.append(int(want))
    elif ident=='n-wideint':
        decl='extern void w(const uint64_t *,const uint64_t *,uint64_t *);\n'
        for j,(a,b,want) in enumerate(re.findall(r'w\(limbs a = (\[[^]]+\]), b = (\[[^]]+\])\) -> r = (\[[^]]+\])',text)):
            aa,bb=values(a),values(b)
            out.append('uint64_t a%d[]={%s},b%d[]={%s},r%d[4];'%(j,','.join(str(x)+'ULL' for x in aa),j,','.join(str(x)+'ULL' for x in bb),j))
            out.append(f'w(a{j},b{j},r{j});printf("[%llu,%llu,%llu,%llu]\\n",(unsigned long long)r{j}[0],(unsigned long long)r{j}[1],(unsigned long long)r{j}[2],(unsigned long long)r{j}[3]);')
            expected.append(values(want))
    elif ident=='n-memintrinsics':
        decl='extern void cp(uint8_t *,const uint8_t *,uint32_t);\n'
        match=re.fullmatch(r'cp\(d, s = \[(\d+), (\d+), …, (\d+)\], (\d+)\) -> d = (\[[^]]+\])',text.strip())
        if not match:raise d.Fail('native vector syntax: '+text)
        first,second,last,n,want=match.groups();seq=list(range(int(first),int(last)+1))
        out=['uint8_t s[]={'+','.join(map(str,seq))+'},d[16]={0};',f'cp(d,s,{n});', 'printf("[");for(int i=0;i<16;i++)printf("%s%u",i?",":"",d[i]);puts("]");'];expected=[values(want)]
    elif ident=='n-atomic':
        decl='extern int32_t at(int32_t *,int32_t);\n'
        for j,(p,x,want,after) in enumerate(re.findall(r'at\(p -> (-?\d+), (-?\d+)\) = (-?\d+), \*p = (-?\d+)',text)):
            out.append(f'int32_t p{j}={p};int32_t r{j}=at(&p{j},{x});printf("[%d,%d]\\n",r{j},p{j});');expected.append([int(want),int(after)])
    elif ident=='n-fmuladd':
        decl='extern double fm(double,double,double);\n'
        for j,(args,answer,bits) in enumerate(re.findall(r'fm\(([^)]+)\) = ([^ ]+) \(0x([a-fA-F0-9]+)\)',text)):
            out.append(f'double r{j}=fm({args});uint64_t b{j};memcpy(&b{j},&r{j},8);printf("%llu\\n",(unsigned long long)b{j});');expected.append(int(bits,16))
    elif ident=='n-fcmp':
        decl='extern _Bool p(double,double);\n'
        for j,(a,b,want) in enumerate(re.findall(r'p\((0x[0-9a-f]+),(0x[0-9a-f]+)\)=(\d+)',text)):
            out.append(f'uint64_t a{j}={a}ULL,b{j}={b}ULL; double x{j},y{j};memcpy(&x{j},&a{j},8);memcpy(&y{j},&b{j},8);printf("%d\\n",p(x{j},y{j}));')
            expected.append(int(want))
    elif ident=='fp-aggregate':
        # LLVM aggregate returns use separate integer return registers; the C ABI
        # packs this struct differently. A module-local wrapper exposes the bits.
        decl='extern uint64_t packed(double);\n'
        m=re.fullmatch(r'p\(([^)]+)\)=\{(-?\d+),(-?\d+)\}; packed=(\d+)',text.strip())
        if not m:raise d.Fail('native aggregate vector syntax: '+text)
        if int(m[4]) != (int(m[2])%256 | (int(m[3])%(1<<32)<<8)):raise d.Fail('native aggregate fields disagree with stated packed result')
        out=[f'printf("%llu\\n",(unsigned long long)packed({m[1]}));'];expected=[int(m[4])];variants=('lift',)
    elif ident=='entry-stack':
        # Contract microvector: exercise the independent seed allocator/adoption.
        decl='extern uint64_t __bennett_seed_entry_stack(void);\n'
        m=re.search(r'malloc\((\d+)\) ptrtoint=(\d+)',text)
        if not m:raise d.Fail('native entry vector syntax: '+text)
        out=['printf("%llu\\n",(unsigned long long)__bennett_seed_entry_stack());'];expected=[int(m[2])];variants=('seed',)
    elif ident=='rung4-mini':
        decl='extern uint8_t q(const uint8_t *,uint64_t,uint32_t);\n'
        image=bytes.fromhex('0007000a0165030704c8052a06630796')
        out.append('uint8_t img[]={'+','.join(map(str,image))+'};')
        for b,want in re.findall(r'q\(img with byte 0 = (\d+), 16, rowid\) for rowid 0\.\.7 = ([01 ]+)',text):
            out.append(f'img[0]={b};printf("[");for(unsigned i=0;i<8;i++)printf("%s%u",i?",":"",q(img,16,i));puts("]");');expected.append([int(x) for x in want.split()])
        variants=('source','materialised')
    else:raise d.Fail('native: unrecognised example '+ident)
    if not expected:raise d.Fail('native: no vectors parsed for '+ident)
    return PREFIX+decl+'int main(void) {\n'+'\n'.join(out)+'\nreturn 0;\n}\n',expected,variants


def check(runner,block):
    from dialect_check_v02 import command,equal
    ident=block['attrs']['native'];body=block['body'];driver,expected,variants=cases(ident,body)
    directory=runner.tmp/('native-'+ident);directory.mkdir(exist_ok=True)
    (directory/'driver.c').write_text(driver)
    for major in ('18','23'):
        clang=runner.frontends[major]/'clang'
        for variant in variants:
            if variant=='seed':
                src=SEEDS/'runtime.c'
            elif variant=='source':
                src=directory/'source.c';src.write_text(runner.block('example','rung4-minidb')['body'])
            else:
                tag='lift' if variant in ('materialised','lift') else 'normalise-in' if variant=='input' else 'normalise-out'
                src=directory/(variant+'.ll')
                text=runner.block(tag,ident)['body']
                # Expose functions to the native driver; no body rewrite.
                text=re.sub(r'\bdefine internal\b','define',text)
                if ident=='fp-aggregate':
                    text += '\ndefine i64 @packed(double %x) {\n %r = call {i8, i32} @p(double %x)\n %a = extractvalue {i8, i32} %r, 0\n %b = extractvalue {i8, i32} %r, 1\n %aa = zext i8 %a to i64\n %bb = zext i32 %b to i64\n %hi = shl i64 %bb, 8\n %v = or i64 %aa, %hi\n ret i64 %v\n}\n'
                src.write_text(d.with_decls(text))
            objects=[src,directory/'driver.c']
            compiler=clang
            if ident=='n-eh' and variant=='input':
                cpp=directory/'throw.cpp';cpp.write_text('extern "C" void may_throw(int x) { if (x&1) throw x; }\n')
                obj=directory/('throw-'+major+'.o')
                command([str(clang)+'++','-O2','-c',cpp,'-o',obj]);objects.append(obj)
                compiler=Path(str(clang)+'++')
            else:
                objects.extend(x for x in [SEEDS/'runtime.c',SEEDS/'softfloat.c'] if x!=src)
            exe=directory/(variant+'-'+major)
            driver_obj=directory/('driver-'+major+'.o')
            command([clang,'-O2','-c',directory/'driver.c','-o',driver_obj])
            objects=[x if x!=directory/'driver.c' else driver_obj for x in objects]
            command([compiler,'-O2','-march=x86-64',*objects,'-o',exe])
            got=[json.loads(line) for line in command([exe]).strip().splitlines()]
            equal(ident+'/'+variant+'/clang'+major,'§1.5 native',expected,got)
            # Every stated fault outcome is executed in its own process.
            if ident=='rung4-mini':
                fault_driver=directory/'fault.c'
                fault_driver.write_text(PREFIX+'extern uint8_t q(const uint8_t *,uint64_t,uint32_t);\nint main(void){uint8_t img[16]={0,7};return q(img,15,0);}\n')
                fault_exe=directory/('fault-'+variant+'-'+major)
                command([clang,'-O2',src,fault_driver,SEEDS/'runtime.c',SEEDS/'softfloat.c','-o',fault_exe])
                from dialect_check_v02 import headless_env
                result=subprocess.run([fault_exe],capture_output=True,text=True,env=headless_env(),timeout=10)
                want=-4 if variant=='source' else 132
                equal(ident+'/'+variant+'/fault','§17.5 native fault',want,result.returncode)


def frontend(runner,block,major):
    from dialect_check_v02 import command,equal,recognise
    ident=block['attrs']['example'];directory=runner.tmp/('frontend-'+ident);directory.mkdir(exist_ok=True)
    if block['lang']!='c':raise d.Fail('checker-unimplemented: frontend '+block['lang'])
    src=directory/'case.c';src.write_text(block['body']);bc=directory/(major+'.bc');ll=directory/(major+'.ll')
    command([runner.frontends[major]/'clang','-O2','-flto','-emit-llvm','-c','-I',d.HEADER.parent,src,'-o',bc])
    command([runner.tc[major]/'opt','-passes=lto<O3>','-S',bc,'-o',ll])
    verdict,info=recognise(ll.read_text(),rmode=block['attrs'].get('rmode'),major=major)
    equal(ident+'/clang'+major,'§1.5 frontend verdict',block['attrs']['verdict'],verdict)
    if ident in runner.by_tag['cc-run']:
        cc=runner.by_tag['cc-run'][ident]['body'];m=re.search(r'native: exit status (\d+)',cc)
        if m and major in ('18','23'):
            exe=directory/('native-'+major)
            command([runner.frontends[major]/'clang','-O2',src,'-o',exe])
            from dialect_check_v02 import headless_env
            result=subprocess.run([exe],capture_output=True,text=True,env=headless_env(),timeout=10)
            equal(ident+'/clang'+major,'§1.5 native exit',int(m[1]),result.returncode)
