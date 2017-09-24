from matcher import PatternMatcher

pm = PatternMatcher()

def test_full_text_match():
    matchers = ["One Two", "Three Five"]
    assert pm.match("One Two", matchers) == True
    assert pm.match("Three Five", matchers) == True
    assert pm.match("One Three", matchers) == False

# def test_partial_text_match():
#     matchers = ["One Two", "Three Four"]
#     assert pm.match("One Two Three", matchers) == True
#     assert pm.match("Two Three Four", matchers) == False

def test_case_sensitivity():
    return False

def test_whitespace_normalisation():
    return False
