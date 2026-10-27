"""Publication-candidate checks; findings are evidence, never an absolute guarantee."""

import gzip
from pathlib import Path
import re

PATTERNS={
    'private_key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'credential_token':re.compile(r'\b(?:sk-[A-Za-z0-9_-]{24,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16})\b'),
    'private_path':re.compile(r'(?:/(?:Users|home)/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\)'),
    'personal_application_link':re.compile(r'/careers/my/application/[0-9]+'),
}
FORBIDDEN={'.pdf','.zip','.sqlite','.sqlite3','.db','.pem','.key','.p12','.pfx'}


def scan_files(root, files=None):
    root=Path(root);files=sorted(files if files is not None else (p for p in root.rglob('*') if p.is_file()))
    findings=[];total=0;largest=[]
    for path in files:
        path=Path(path);relative=str(path.relative_to(root));size=path.stat().st_size;total+=size;largest.append((size,relative))
        if path.is_symlink() or path.suffix.lower() in FORBIDDEN or path.name.startswith('.env'):
            findings.append({'file':relative,'kind':'private_or_binary_filename','line':None});continue
        opener=gzip.open if path.suffix=='.gz' else open
        try:
            with opener(path,'rt',encoding='utf-8',newline='') as stream:
                found=set()
                for line_number,line in enumerate(stream,1):
                    for kind,pattern in PATTERNS.items():
                        if kind not in found and pattern.search(line):
                            findings.append({'file':relative,'kind':kind,'line':line_number});found.add(kind)
        except (UnicodeError,OSError):findings.append({'file':relative,'kind':'unexpected_binary_or_encoding','line':None})
        if size>50*1024*1024:findings.append({'file':relative,'kind':'large_file_review','line':None})
    return {'files_scanned':len(files),'bytes':total,'findings':findings,'passed':not findings,
        'largest_files':[{'path':name,'bytes':size} for size,name in sorted(largest,reverse=True)[:5]],
        'limitation':'Pattern and provenance checks reduce accidental disclosure; final human content/ownership review remains required.'}


def synthetic_identity_check(connection):
    violations=[]
    for row in connection.execute('SELECT candidate_id,display_name,contact_email FROM Candidate ORDER BY candidate_id'):
        if not re.fullmatch(r'Synthetic Candidate [0-9]{6}',row['display_name']) or row['contact_email']!=f"candidate{row['candidate_id'][-6:]}@example.invalid":violations.append(row['candidate_id'])
    for row in connection.execute('SELECT staff_id,display_name FROM Staff ORDER BY staff_id'):
        if not row['display_name'].startswith('Synthetic '):violations.append(row['staff_id'])
    return {'passed':not violations,'identity_violations':violations,'email_domain':'example.invalid',
        'provenance':'All candidate identities and recruitment records are synthetic; no scraped profiles, resumes, confidential records or external personal datasets.'}
