"""Git-free, strict publication-tree content scan. Never prints matched values."""
import argparse
from collections import Counter
import getpass
import gzip
import json
from pathlib import Path
import re
import socket

from yottaflex.privacy import PATTERNS,FORBIDDEN

ROOT=Path(__file__).resolve().parents[1]
EMAIL=re.compile(r'(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
SAFE_DOMAINS={'example.invalid','local.invalid','yottaflex.ai'}
SAFE_EXAMPLES={'example@example.com'} # Literal rejected test input, not a real contact.
LOCAL_ROOTS={'.git','.venv','output','tmp','inputs','data','__pycache__','.pytest_cache','node_modules','.idea'}


def scan(root=ROOT,private_identities=()):
    root=Path(root);issues=[];count=total=expanded=compressed=0
    patterns=dict(PATTERNS)
    patterns['private_path']=re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+(?:/|\b)|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+(?:\\|\b)')
    patterns['additional_token']=re.compile(r'\b(?:gh[ousr]_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{24,})\b')
    identities=[('current_user_identifier',getpass.getuser()),('host_identifier',socket.gethostname())]
    identities += [('private_metadata_identity',value) for value in private_identities if isinstance(value,str)]
    for index,(kind,value) in enumerate(identities):
        if len(value)>=4:patterns[kind+'_'+str(index)]=re.compile(r'(?<![A-Za-z0-9_])'+re.escape(value)+r'(?![A-Za-z0-9_])',re.I)
    for path in sorted(root.rglob('*')):
        name=str(path.relative_to(root));parts=Path(name).parts
        if path.is_symlink():issues.append({'file':name,'line':None,'kind':'symlink'});continue
        if not path.is_file():continue
        count+=1;size=path.stat().st_size;total+=size
        if any(part in LOCAL_ROOTS for part in parts) or path.name in {'.DS_Store','Thumbs.db'} or path.suffix.lower() in FORBIDDEN or path.suffix.lower() in {'.pyc','.log'} or path.name.startswith('.env') and path.name!='.env.example':
            issues.append({'file':name,'line':None,'kind':'unwanted_source_metadata_or_local_file'})
        if size>50*1024*1024:issues.append({'file':name,'line':None,'kind':'large_file_review'})
        try:
            data=path.read_bytes()
            if path.suffix=='.gz':data=gzip.decompress(data);compressed+=1
            expanded+=len(data);text=data.decode('utf-8')
        except (UnicodeError,OSError,EOFError):issues.append({'file':name,'line':None,'kind':'unexpected_binary_or_encoding'});continue
        seen=set()
        for line_number,line in enumerate(text.splitlines(),1):
            for kind,pattern in patterns.items():
                if kind not in seen and pattern.search(line):issues.append({'file':name,'line':line_number,'kind':kind});seen.add(kind)
            if 'non_allowlisted_email' not in seen and any(match.group().lower().split('@')[-1] not in SAFE_DOMAINS and match.group().lower() not in SAFE_EXAMPLES for match in EMAIL.finditer(line)):
                issues.append({'file':name,'line':line_number,'kind':'non_allowlisted_email'});seen.add('non_allowlisted_email')
    return {'passed':not issues,'files_scanned':count,'stored_bytes':total,'expanded_bytes_scanned':expanded,'compressed_files_decompressed':compressed,'findings':issues,'counts_by_kind':dict(Counter(i['kind'] for i in issues)),
        'private_metadata_identities_checked':len(private_identities),'policy':'Every file in publication tree; no Git required or invoked; gzip decompressed. Reports only relative location/category, never matched values. Official employer email domains and literal synthetic negative-test email are allowlisted.',
        'limits':'Pattern/known-identity scans cannot guarantee all privacy/security/ownership. Synthetic identity SQL checks and personal final content review are separate. No matched private metadata is serialized.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--private-identities',type=Path)
    a=p.parse_args();identities=json.loads(a.private_identities.read_text()) if a.private_identities else []
    result=scan(private_identities=identities);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('passed','files_scanned','stored_bytes','expanded_bytes_scanned','compressed_files_decompressed','counts_by_kind')},indent=2))
    raise SystemExit(0 if result['passed'] else 1)
