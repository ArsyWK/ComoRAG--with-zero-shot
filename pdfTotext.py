from pypdf import PdfReader
import pathlib
import json
import re
workdir =pathlib.Path("./dataset/laskar_pelangi/laskar_pelangi_1")

path = pathlib.Path("./dataset/laskar_pelangi/laskar_pelangi_1/laskar pelangi.pdf")
book = PdfReader(path)
extracted_text = "\n".join([page.extract_text() for page in book.pages if page.extract_text()])

with open(workdir/f"{path.name}.txt",'w',encoding="utf-8") as wor:
    wor.write(extracted_text)


parts = [p for p in re.split(r"(?<=\.)\s+", extracted_text)]
valid_segment= [s for s in parts if len(s.split())>=6]

with open(workdir/f"corpus.jsonl",'w',encoding="utf-8") as wor:
    for i, segment in enumerate(valid_segment, 1):
        title_words = segment.split()[:4]
        title = "".join(title_words)

        record = {
            "id":i,
            "doc_id": 1,
            "title": title,
            "contents": f"{title},{segment}"
        }
        wor.write(json.dumps(record,ensure_ascii=False)+"\n")






