"""Recompute the stored hashes of the draft's tagged ISA objects with the reference interpreter."""
import json,re,subprocess,sys,tempfile
from pathlib import Path

def run(exe,verb,path):
    p=subprocess.run([exe,verb,path],capture_output=True,text=True)
    if p.returncode:raise SystemExit(f'{verb} {path}: {p.stderr.strip()}')
    return json.loads(p.stdout)

def main(spec,exe,scratch):
    text=Path(spec).read_text();changed=0
    names={}
    def fix(m):
        nonlocal changed
        info,body=m[1],m[2]
        tag=re.search(r'\bobject=(\S+)',info)
        if not tag:return m[0]
        path=Path(scratch)/(tag[1]+'.bisa');path.write_text(body)
        syms=run(exe,'hash',path)['symbols'];lines=body.split('\n')
        i=lines.index('section symbols')+1;table=json.loads(lines[i])
        for s in table.values():s['interface_hash']=syms[s['name']]['interface_hash']
        new=json.dumps(table,sort_keys=True,separators=(',',':'))
        if new!=lines[i]:changed+=1
        lines[i]=new;names[tag[1]]=syms
        return '```'+info+'\n'+'\n'.join(lines)+'```'
    text=re.sub(r'^```([^\n]*)\n(.*?)^```[ \t]*$',fix,text,flags=re.S|re.M)
    def fixhash(m):
        ident=m[1]
        out=[]
        for ln in m[2].strip().split('\n'):
            n=ln.split()[0];out.append(n+' '+names[ident][n]['interface_hash'])
        return '```text hash='+ident+'\n'+'\n'.join(out)+'\n```'
    text=re.sub(r'^```\w* hash=(\S+)\n(.*?)^```[ \t]*$',fixhash,text,flags=re.S|re.M)
    Path(spec).write_text(text)
    print('objects rehashed:',changed)

if __name__=='__main__':main(*sys.argv[1:])
