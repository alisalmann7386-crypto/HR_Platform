import hashlib
from pathlib import Path
from pypdf import PdfReader

def load_documents(folder):
    documents=[];errors=[]
    paths=sorted(Path(folder).glob('*.pdf'))
    if not paths: raise ValueError('No policy PDF files found.')
    for path in paths:
        try:
            reader=PdfReader(path)
            if reader.is_encrypted: raise ValueError('Encrypted PDF')
            readable=0
            for page_num,page in enumerate(reader.pages,1):
                text=page.extract_text() or ''
                if text.strip():
                    documents.append({'document_name':path.name,'page_number':page_num,'text':text,'document_sha256':hashlib.sha256(path.read_bytes()).hexdigest()});readable+=1
            if not readable: raise ValueError('Empty/scanned PDF; OCR required')
        except Exception as e:errors.append({'document':path.name,'error':str(e)})
    if not documents:raise ValueError('No readable policies: '+str(errors))
    return documents,errors
