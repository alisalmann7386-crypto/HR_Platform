import re
import hashlib

def chunk_documents(pages,chunk_size=140,chunk_overlap=25):
    if not 0<=chunk_overlap<chunk_size:raise ValueError('Overlap must be nonnegative and smaller than chunk size.')
    chunks=[]
    for page in pages:
        section='Document introduction';buf=[];sections=[]
        for line in page['text'].splitlines():
            line=line.strip()
            if re.match(r'^(?:\d+\.\d+|\d+\.)\s+\S',line):
                if buf:sections.append((section,' '.join(buf)))
                section=line;buf=[]
            elif line and not re.match(r'^(Page \d+ of|WAI-HR-\d+ \|)',line):buf.append(line)
        if buf:sections.append((section,' '.join(buf)))
        for section,text in sections:
            words=text.split()
            for start in range(0,len(words),chunk_size-chunk_overlap):
                chunk=' '.join(words[start:start+chunk_size])
                if not chunk:continue
                identity=f'{page["document_name"]}|{page["page_number"]}|{section}|{start}|{chunk}'
                chunks.append({k:v for k,v in page.items() if k!='text'}|{'section':section,'chunk_id':hashlib.sha256(identity.encode()).hexdigest()[:16],'text':chunk})
                if start+chunk_size>=len(words):break
    return chunks
