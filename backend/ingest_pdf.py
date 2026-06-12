import sys
import json
import urllib.request
from pypdf import PdfReader

pdf_path = sys.argv[1]
reader = PdfReader(pdf_path)
text = "\n".join(page.extract_text() for page in reader.pages)

req = urllib.request.Request(
    "http://localhost:8000/ingest",
    data=json.dumps({"text": text}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
print(resp.read().decode())
