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


def test_sections_under_different_headings_are_not_merged():
    # Even though combined they're well under max_chars, two unrelated
    # sections should never end up smeared into the same chunk.
    text = "## Section A\n\nShort content A.\n\n## Section B\n\nShort content B."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## Section A\n\nShort content A.", "## Section B\n\nShort content B."]


def test_content_before_first_heading_is_its_own_section():
    text = "Intro paragraph before any heading.\n\n## Section A\n\nContent A."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["Intro paragraph before any heading.", "## Section A\n\nContent A."]


def test_paragraphs_within_one_section_are_still_grouped_together():
    text = "## Section A\n\nFirst paragraph.\n\nSecond paragraph."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## Section A\n\nFirst paragraph.\n\nSecond paragraph."]


def test_nested_heading_levels_each_start_a_new_section():
    text = "## Parent\n\nParent content.\n\n### Child\n\nChild content."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## Parent\n\nParent content.", "### Child\n\nChild content."]


def test_bare_heading_with_no_body_is_folded_into_next_section():
    # A heading immediately followed by a subheading (no content of its own)
    # must not become a standalone chunk containing only a section title.
    text = "## 5. Taking Leave\n\n### 5.1 Access and Timing\n\nContent here."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## 5. Taking Leave\n\n### 5.1 Access and Timing\n\nContent here."]


def test_multiple_consecutive_bare_headings_are_all_folded_forward():
    text = "## A\n\n### B\n\n#### C\n\nActual content."
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## A\n\n### B\n\n#### C\n\nActual content."]


def test_trailing_bare_heading_with_nothing_after_it_is_kept_as_is():
    text = "## Section A\n\nSome real content here.\n\n## Trailing Heading"
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["## Section A\n\nSome real content here.", "## Trailing Heading"]
