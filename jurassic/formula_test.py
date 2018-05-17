import formula

def test_is_pooled():
    row = lambda x:{'Is Pooled? (Y/N)':x}
    tests = [('Y', True)
            ,('yes', True)
            ,('Yes', True)
            ,(' Y ', True)
            ,('no', False)
            ,('  ', False)
            ,('', False)
            ,('N', False)
            ]
    for t in tests:
        assert formula.is_pooled(row(t[0])) == t[1]

def test_fossil_amount_formula():
    expected = '=IF(F17="0",0,H17)'
    assert expected == formula.fossil_amount(17, 'F', 'H')

def test_verification_formula():
    expected = '=IF(OR(NOT(A3="0"),NOT(B3="0")),C3,A3)'
    assert expected == formula.verification(3, 'A', 'B', 'C')

    expected = '=IF(OR(NOT(D12="0"),NOT(E12="0")),B12,D12)'
    assert expected == formula.verification(12, 'D', 'E', 'B')

def test_pattern_match_formula():
    expected1 = '=ARRAYFORMULA(IFS(REGEXMATCH(A1, "abc"), "A", REGEXMATCH(A1, "def"), "B", TRUE, "0"))'
    expected2 = '=ARRAYFORMULA(IFS(REGEXMATCH(B:B, "abc"), "A", REGEXMATCH(B:B, "def"), "B", TRUE, "0"))'
    categories = [{'name':'A', 'pattern':'abc'}
                 ,{'name':'B', 'pattern':'def'}]
    assert formula.pattern_match("A1", categories) == expected1
    assert formula.pattern_match("B:B", categories) == expected2

def test_pool_match_formula():
    expected = '=ARRAYFORMULA(IFS(A:A="Company 1", "yes", A:A="Company 3", "yes", TRUE, ""))'
    pooled_info = [{'Is Pooled? (Y/N)':'Y', 'Name':'Company 1'}
                  ,{'Is Pooled? (Y/N)':'N', 'Name':'Company 2'}
                  ,{'Is Pooled? (Y/N)':'Y', 'Name':'Company 3'}]
    assert formula.pooled_match("A:A", pooled_info) == expected
    assert formula.pooled_match("A:A", []) == None
    assert formula.pooled_match("A:A", [{'Is Pooled? (Y/N)':'N'}]) == None


def test_largest_value():
    expected = "=LARGE('Full Data'!G:G,1)"
    assert formula.largest_value('Full Data', 'G', 1) == expected

def test_largest_value_name():
    expected = "=INDEX('Full Data'!F:F,MATCH(LARGE('Full Data'!G:G,1),'Full Data'!G:G,0))"
    assert formula.largest_value_name('Full Data', 'G', 'F', 1) == expected
