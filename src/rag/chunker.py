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


def fit_semantic_chunks(chunks, tokenizer, max_tokens, overlap_words=25):
    """Fit the actual encoder budget while preserving exact source word spans."""
    def length(text):
        return len(tokenizer.encode(text, add_special_tokens=True, truncation=False, verbose=False))
    result = []
    for chunk in chunks:
        prefix = chunk['section']+' '
        if length(prefix+chunk['text']) <= max_tokens:
            result.append(chunk)
            continue
        words = chunk['text'].split()
        start = 0
        while start < len(words):
            low, high, end = start+1, len(words), start
            while low <= high:
                middle = (low+high)//2
                if length(prefix+' '.join(words[start:middle])) <= max_tokens:
                    end, low = middle, middle+1
                else:high = middle-1
            if end == start:raise ValueError('Policy heading or unbroken word exceeds the embedding token budget.')
            text = ' '.join(words[start:end])
            identity = f"{chunk['chunk_id']}|tokens|{start}|{text}"
            result.append(dict(chunk, text=text, chunk_id=hashlib.sha256(identity.encode()).hexdigest()[:16]))
            if end == len(words):break
            start = end-min(overlap_words, (end-start)//2)
    return result
