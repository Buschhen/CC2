import fitz
import tiktoken
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY", "test")

client = OpenAI(api_key=OPENAI_KEY)

MAX_TOKENS_PER_CHUNK = 3000

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def estimate_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-4")
    return len(enc.encode(text))

def chunk_text(text, max_tokens=MAX_TOKENS_PER_CHUNK):
    paragraphs = text.split('\n\n')
    chunks, current = [], ""

    for para in paragraphs:
        if estimate_tokens(current + para) > max_tokens:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para

    if current.strip():
        chunks.append(current.strip())
    return chunks

def summarize_chunk(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize the following text clearly and concisely."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def summarize_pdf(file_bytes):
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)
    print(f"📄 Processing {len(chunks)} chunk(s)...")

    summaries = [summarize_chunk(chunk) for chunk in chunks]
    final_summary = summarize_chunk("\n\n".join(summaries))
    return final_summary
