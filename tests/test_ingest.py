from ingestion.ingest import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_single_short_paragraph_is_one_chunk():
    text = "This is the only paragraph."
    assert chunk_text(text, max_chars=1000) == [text]


def test_paragraphs_grouped_together_when_under_limit():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["First paragraph.\n\nSecond paragraph.\n\nThird paragraph."]


def test_splits_into_new_chunk_once_limit_would_be_exceeded():
    # Each paragraph is 10 chars; max_chars=25 fits two but not three per chunk.
    paragraphs = ["a" * 10, "b" * 10, "c" * 10]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, max_chars=25)
    assert chunks == ["a" * 10 + "\n\n" + "b" * 10, "c" * 10]


def test_oversized_single_paragraph_is_kept_whole():
    # A single paragraph longer than max_chars still becomes its own chunk,
    # since this naive chunker never splits inside a paragraph.
    long_paragraph = "word " * 500
    chunks = chunk_text(long_paragraph, max_chars=100)
    assert chunks == [long_paragraph.strip()]


def test_blank_paragraphs_are_dropped():
    text = "First paragraph.\n\n   \n\nSecond paragraph."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["First paragraph.\n\nSecond paragraph."]


def test_all_original_content_is_preserved_across_chunks():
    paragraphs = [f"paragraph {i} " * 20 for i in range(5)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, max_chars=200)
    rejoined = "\n\n".join(chunks)
    for paragraph in paragraphs:
        assert paragraph.strip() in rejoined
