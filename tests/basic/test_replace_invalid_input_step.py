from nerdd_link.steps.replace_invalid_input_step import ReplaceInvalidInputStep


def test_replaces_non_text_unknown_input():
    record = {"input_type": "unknown", "input_text": object()}

    result = next(ReplaceInvalidInputStep("source-1")(iter([record])))

    assert result["input_text"] == "source-1"


def test_preserves_text_unknown_input_and_valid_input():
    records = [
        {"input_type": "unknown", "input_text": "invalid SMILES"},
        {"input_type": "smiles", "input_text": object()},
    ]

    results = list(ReplaceInvalidInputStep("source-1")(iter(records)))

    assert results[0]["input_text"] == "invalid SMILES"
    assert results[1]["input_text"] is records[1]["input_text"]
