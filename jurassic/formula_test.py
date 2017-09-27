import formula

def test_verification_formula():
    expected = '=IF(OR(NOT(A3="0"),NOT(B3="0")),C3,A3)'
    assert expected == formula.verification_formula(3, 'A', 'B', 'C')

    expected = '=IF(OR(NOT(D12="0"),NOT(E12="0")),B12,D12)'
    assert expected == formula.verification_formula(12, 'D', 'E', 'B')

def test_pattern_match_formula():
    expected = '=IFS(REGEXMATCH(A1, "abc"), "A", REGEXMATCH(A1, "def"), "B")'
    assert formula.pattern_match_formula("A1", [["A", "abc"], ["B", "def"]]) == expected
