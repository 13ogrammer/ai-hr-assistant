from unittest.mock import MagicMock, patch

from generation.generate import build_prompt, generate_answer
from models.chunk import RetrievedChunk


def make_chunk(source="policy.md", chunk_index=0, content="Some policy text.", distance=0.1):
    return RetrievedChunk(source=source, chunk_index=chunk_index, content=content, distance=distance)


def test_build_prompt_includes_the_question():
    prompt = build_prompt("How much annual leave do I get?", [make_chunk()])
    assert "How much annual leave do I get?" in prompt


def test_build_prompt_includes_chunk_content():
    prompt = build_prompt("question", [make_chunk(content="Annual leave is 4 weeks.")])
    assert "Annual leave is 4 weeks." in prompt


def test_build_prompt_tags_each_chunk_with_its_source():
    prompt = build_prompt("question", [make_chunk(source="02_ANNUAL_LEAVE_POLICY.md")])
    assert "[Source: 02_ANNUAL_LEAVE_POLICY.md]" in prompt


def test_build_prompt_keeps_multiple_chunks_in_order():
    chunks = [make_chunk(source="a.md", content="Content A"), make_chunk(source="b.md", content="Content B")]
    prompt = build_prompt("question", chunks)
    assert prompt.index("Content A") < prompt.index("Content B")


def test_build_prompt_with_no_chunks_still_includes_the_question():
    prompt = build_prompt("question with no context", [])
    assert "question with no context" in prompt


def test_generate_answer_returns_the_model_response_text():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="4 weeks."))]

    with patch("generation.generate.OpenAI") as mock_openai_class:
        mock_openai_class.return_value.chat.completions.create.return_value = fake_response
        answer = generate_answer("How much leave?", [make_chunk()])

    assert answer == "4 weeks."


def test_generate_answer_sends_system_and_user_messages_with_context():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="irrelevant"))]

    with patch("generation.generate.OpenAI") as mock_openai_class:
        mock_client = mock_openai_class.return_value
        mock_client.chat.completions.create.return_value = fake_response
        generate_answer("How much leave?", [make_chunk(content="4 weeks annual leave.")])

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    messages = kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "4 weeks annual leave." in messages[1]["content"]
    assert "How much leave?" in messages[1]["content"]
