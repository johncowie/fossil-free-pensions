import formula

def test_pattern_match_formula():
    expected = '=IFS(REGEXMATCH(A1, "abc"), "A", REGEXMATCH(A1, "def"), "B")'
    assert formula.pattern_match_formula("A1", [["A", "abc"], ["B", "def"]]) == expected
