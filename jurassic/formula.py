def verification_formula(row, oil_col, coal_col, name_col):
    row_str = str(row)
    oil_cell = oil_col+row_str
    coal_cell = coal_col+row_str
    name_cell = name_col+row_str
    return '=IF(OR(NOT({0}="0"),NOT({1}="0")),{2},{0})'.format(oil_cell, coal_cell, name_cell)

def pattern_match_formula(cell_id, patterns):
    f = lambda pair:'REGEXMATCH({0}, "{1}"), "{2}"'.format(cell_id, pair[1], pair[0])
    s = ', '.join(map(f, patterns))
    return "=IFS({0})".format(s)
