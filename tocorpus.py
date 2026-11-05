import json
import os
from pathlib import Path
txt_file_path = "./dataset/laskar_pelangi/laskar_pelangi_1/85jkr_harrypotter_1.txt"
output_corpus_path = "./dataset/laskar_pelangi/laskar_pelangi_1/corpus.jsonl"


def create_corpus_from_txt(txt_path, output_path, chunk_size_words=200):
    with open(txt_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

    corpus_entries = []
    current_chunk = []
    current_word_count = 0
    chunk_idx = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        current_chunk.append(paragraph)
        current_word_count += len(words)

        if current_word_count >= chunk_size_words:
            chunk_text = " ".join(current_chunk)

            first_sentence = chunk_text.split('.')[0][:50].strip()

            corpus_entries.append({
                "id": chunk_idx,
                "doc_id": chunk_idx + 1,
                "title": f'"{first_sentence}"',
                "contents": f'"{chunk_text}"'
            })

            chunk_idx += 1
            current_chunk = []
            current_word_count = 0


    if current_chunk:
        chunk_text = " ".join(current_chunk)
        first_sentence = chunk_text.split('.')[0][:50].strip()
        corpus_entries.append({
            "id": chunk_idx,
            "doc_id": chunk_idx + 1,
            "title": f'"{first_sentence}"',
            "contents": f'"{chunk_text}"'
        })


    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in corpus_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


create_corpus_from_txt(txt_file_path, output_corpus_path)