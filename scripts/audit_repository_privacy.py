"""Read-only tree/reachable-history review; reports locations, never matched values."""
import argparse
from collections import Counter
import getpass
import gzip
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess

from yottaflex.privacy import PATTERNS,FORBIDDEN

EMAIL=re.compile(r'(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
SAFE_DOMAINS={'example.invalid','local.invalid','yottaflex.ai'}
SAFE_EXAMPLES={'example@example.com'} # Deliberately rejected schema-test input, not a person.


def git(*args):
    return subprocess.check_output(['git',*args])


def findings(data,name):
    result=[]
    if Path(name).suffix.lower() in FORBIDDEN or Path(name).name.startswith('.env') and Path(name).name!='.env.example':
        result.append({'kind':'private_or_binary_filename','line':None})
    if len(data)>50*1024*1024:result.append({'kind':'large_file_review','line':None})
    try:
        content=gzip.decompress(data) if name.endswith('.gz') else data
        text=content.decode('utf-8')
    except (UnicodeError,OSError,EOFError):
        return result+[{'kind':'unexpected_binary_or_encoding','line':None}]
    patterns=dict(PATTERNS)
    for kind,value in [('user_identifier',getpass.getuser()),('host_identifier',socket.gethostname())]:
        if len(value)>=4:patterns[kind]=re.compile(r'(?<![A-Za-z0-9_])'+re.escape(value)+r'(?![A-Za-z0-9_])',re.I)
    seen=set()
    for number,line in enumerate(text.splitlines(),1):
        for kind,pattern in patterns.items():
            if kind not in seen and pattern.search(line):
                result.append({'kind':kind,'line':number});seen.add(kind)
        if 'non_allowlisted_email' not in seen and any(match.group().lower().split('@')[-1] not in SAFE_DOMAINS and match.group().lower() not in SAFE_EXAMPLES for match in EMAIL.finditer(line)):
            result.append({'kind':'non_allowlisted_email','line':number});seen.add('non_allowlisted_email')
    return result


def audit():
    current=[];paths=git('ls-files','-z').decode().split('\0')
    for name in filter(None,paths):
        path=Path(name)
        issues=findings(path.read_bytes(),name)
        if path.is_symlink():issues.append({'kind':'symlink_review','line':None})
        current.extend({'file':name,**issue} for issue in issues)
    revisions=git('rev-list','--reverse','--all').decode().splitlines()
    blobs={};commit_issues=[]
    for revision in revisions:
        meta=git('show','-s','--format=%an%n%ae%n%cn%n%ce%n%B',revision)
        fields=meta.decode().split('\n',4)
        for index,field in enumerate(('author_name','author_email','committer_name','committer_email')):
            value=fields[index]
            if field.endswith('_name') and value!='Codex':
                commit_issues.append({'commit':revision,'field':field,'kind':'non_generic_person_name','line':index+1})
            if field.endswith('_email'):
                commit_issues.extend({'commit':revision,'field':field,**item,'line':index+1} for item in findings(value.encode('utf-8'),'commit-metadata.txt'))
        commit_issues.extend({'commit':revision,'field':'message',**item} for item in findings((fields[4] if len(fields)>4 else '').encode('utf-8'), 'commit-message.txt'))
        for entry in git('ls-tree','-r','-z',revision).split(b'\0'):
            if not entry:continue
            info,raw_name=entry.split(b'\t',1);mode,kind,oid=info.decode().split();name=raw_name.decode()
            if kind!='blob':continue
            item=blobs.setdefault(oid,{'files':set(),'commits':[]});item['files'].add(name);item['commits'].append(revision)
    historic=[]
    for oid,item in blobs.items():
        data=git('cat-file','blob',oid)
        for name in sorted(item['files']):
            for issue in findings(data,name):historic.append({'blob':oid,'file':name,'commits':item['commits'],**issue})
    return {'current_revision':git('rev-parse','HEAD').decode().strip(),'current_files_scanned':len([p for p in paths if p]),
        'current_findings':current,'reachable_commits_scanned':len(revisions),'unique_file_blobs_scanned':len(blobs),
        'historical_findings':historic,'commit_metadata_findings':commit_issues,
        'current_counts_by_kind':dict(Counter(i['kind'] for i in current)),
        'historical_counts_by_kind':dict(Counter(i['kind'] for i in historic)),
        'publication_safe':not(current or historic or commit_issues),
        'policy':'All reachable refs/commits, unique blob contents (gzip decompressed), paths and author/committer/messages. Reports only relative file/line/blob/commit/kind, never matched private values. Official employer public email and clearly synthetic test examples allowlisted.',
        'limitations':'Pattern/current-user-host checks cannot prove absence of all sensitive content. No account-wide/dangling-object export or human security audit; Git objects and history not changed.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('current_files_scanned','reachable_commits_scanned','unique_file_blobs_scanned','current_counts_by_kind','historical_counts_by_kind','publication_safe')},indent=2))
