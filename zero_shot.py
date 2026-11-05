import json
import re
from openai import OpenAI
import tiktoken

client = OpenAI(
    base_url="http://192.168.0.105:8000/v1",
    api_key="EMPTY"
)

book_path = "./dataset/laskar_pelangi/laskar_pelangi_1/laskar pelangi.pdf.txt"
qas_path = "./dataset/laskar_pelangi/laskar_pelangi_1/qas.jsonl"
output_path = "./dataset/laskar_pelangi/laskar_pelangi_1/qas_golden.jsonl"

MAX_TOTAL_TOKENS = 8192
SAFETY_MARGIN = 2500

questions = []
with open(qas_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            questions.append(json.loads(line))


with open(book_path, "r", encoding="utf-8") as f:
    full_book_text = f.read()


tokenizer = tiktoken.get_encoding("o200k_base")


def truncate_text_to_token_limit(text, max_tokens):
    tokens = tokenizer.encode(text)
    token_count = len(tokens)

    if token_count > max_tokens:
        print(f" From {token_count} tokens, shrinked down to {max_tokens} tokens.")
        truncated_tokens = tokens[:max_tokens]
        text = tokenizer.decode(truncated_tokens)
    else:
        print(f" Token sufficient {token_count} tokens")

    return text


max_book_tokens = MAX_TOTAL_TOKENS - SAFETY_MARGIN
book_context = truncate_text_to_token_limit(full_book_text, max_book_tokens)

prompt = f"""
You are an expert annotator. Read the following text context from the book carefully and answer the questions based ONLY on the text.

--- BOOK CONTEXT ---
{book_context}

--- QUESTIONS ---
{json.dumps(questions, indent=2)}

--- INSTRUCTIONS ---
For each question, output a JSON array where each object contains:
- "id": string matching the input question id
- "question": the original question text
- "golden_answers": an array of 2 short, highly accurate factual answers derived from the text.

Respond ONLY with valid JSON inside a code block, like this:
[
  {{"id": "0", "question": "example question", "golden_answers": ["Answer 1", "Answer 2"]}}
]
"""

full_prompt_tokens = len(tokenizer.encode(prompt))
print(f"Total prompt token count: {full_prompt_tokens} / {MAX_TOTAL_TOKENS}")


def safe_parse_json(text):
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        repaired = re.sub(r',?\s*"[^"]*$', '', cleaned)
        if not repaired.endswith("]"):
            repaired += "]"
        return json.loads(repaired)

try:
    response = client.chat.completions.create(
        model="qwen-instruct",
        messages=[
            {"role": "system", "content": "You are a precise data annotation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1500
    )

    output_text = response.choices[0].message.content
    print(output_text)

    golden_data = safe_parse_json(output_text)

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in golden_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


except Exception as e:
    print(f"\nAPI Error: {e}")