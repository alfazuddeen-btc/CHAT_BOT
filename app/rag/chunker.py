def chunk_document(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    chunks = []

    text = remove_code_blocks(text)
    text = remove_metadata(text)

    sentences = text.split(". ")
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:  
            continue

        current_chunk += sentence + ". "

        if len(current_chunk) >= chunk_size:
            if len(current_chunk.strip()) > 50:
                chunks.append(current_chunk.strip())
            current_chunk = sentence[-overlap:] if len(sentence) > overlap else sentence

    if len(current_chunk.strip()) > 50:
        chunks.append(current_chunk.strip())

    return chunks

def remove_code_blocks(text: str) -> str:
    import re
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'<code>[\s\S]*?</code>', '', text)
    return text

def remove_metadata(text: str) -> str:
    import re
    text = re.sub(r'"metadata":\s*\{[^}]*\}', '', text)
    text = re.sub(r'\{[^}]*source[^}]*\}', '', text)
    return text