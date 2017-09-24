def pattern_match_formula(cell_id, patterns):
    f = lambda pair:'REGEXMATCH({0}, "{1}"), "{2}"'.format(cell_id, pair[1], pair[0])
    s = ', '.join(map(f, patterns))
    return "=IFS({0})".format(s)
