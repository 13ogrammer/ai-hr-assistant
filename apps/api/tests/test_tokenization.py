"""Pure unit tests for TokenMap - no DB, no OpenAI, no generate_answer."""

from generation.tokenization import TokenMap


def test_employee_token_is_stable_for_the_same_id():
    token_map = TokenMap()
    first = token_map.employee_token("maya.chen", "Maya Chen")
    second = token_map.employee_token("maya.chen", "Maya Chen")
    assert first == second


def test_employee_token_differs_across_employees():
    token_map = TokenMap()
    maya_token = token_map.employee_token("maya.chen", "Maya Chen")
    tom_token = token_map.employee_token("tom.richards", "Tom Richards")
    assert maya_token != tom_token


def test_resolve_employee_id_reverses_a_known_token():
    token_map = TokenMap()
    token = token_map.employee_token("maya.chen", "Maya Chen")
    assert token_map.resolve_employee_id(token) == "maya.chen"


def test_resolve_employee_id_passes_through_an_unrecognized_value_unchanged():
    token_map = TokenMap()
    assert token_map.resolve_employee_id("not.a.known.token") == "not.a.known.token"


def test_value_token_produces_distinct_tokens_for_repeated_calls():
    token_map = TokenMap()
    first = token_map.value_token("SALARY", "$92,000")
    second = token_map.value_token("SALARY", "$165,000")
    assert first != second


def test_detokenize_substitutes_an_employee_token_with_the_real_name():
    token_map = TokenMap()
    token = token_map.employee_token("maya.chen", "Maya Chen")
    assert token_map.detokenize(f"{token}'s salary is confidential.") == "Maya Chen's salary is confidential."


def test_detokenize_substitutes_a_value_token_with_the_real_display_string():
    token_map = TokenMap()
    token = token_map.value_token("SALARY", "$420,000")
    assert token_map.detokenize(f"The salary is {token}.") == "The salary is $420,000."


def test_detokenize_does_not_confuse_a_token_with_a_longer_token_sharing_its_prefix():
    # value_token's counter means SALARY_1 is a literal substring of SALARY_10
    # - a naive str.replace() would mangle SALARY_10 while replacing SALARY_1.
    token_map = TokenMap()
    first = token_map.value_token("SALARY", "$1")
    for _ in range(8):
        token_map.value_token("SALARY", "$0")  # burn SALARY_2..SALARY_9
    tenth = token_map.value_token("SALARY", "$10")

    result = token_map.detokenize(f"Values: {first} and {tenth}.")

    assert result == "Values: $1 and $10."


def test_detokenize_handles_multiple_tokens_in_the_same_text():
    token_map = TokenMap()
    emp_token = token_map.employee_token("michael.hartley", "Michael Hartley")
    salary_token = token_map.value_token("SALARY", "$420,000")
    text = f"{emp_token}'s salary is {salary_token}."
    assert token_map.detokenize(text) == "Michael Hartley's salary is $420,000."
