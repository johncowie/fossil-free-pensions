def fossil_amount(row, verification_column, amount_column):
    rowStr = str(row)
    ver_cell = verification_column + rowStr
    am_cell = amount_column + rowStr
    return '=IF({0}="0",0,{1})'.format(ver_cell, am_cell)

def verification(row, oil_col, coal_col, name_col):
    row_str = str(row)
    oil_cell = oil_col+row_str
    coal_cell = coal_col+row_str
    name_cell = name_col+row_str
    return '=IF(OR(NOT({0}="0"),NOT({1}="0")),{2},{0})'.format(oil_cell, coal_cell, name_cell)

def pattern_match(cell_id, patterns):
    f = lambda pair:'REGEXMATCH({0}, "{1}"), "{2}"'.format(cell_id, pair['pattern'], pair['name'])
    s = ', '.join(map(f, patterns))
    return '=ARRAYFORMULA(IFS({0}, TRUE, "0"))'.format(s)

def largest_value(worksheet_name, column, rank):
    return "=LARGE('{0}'!{1}:{1},{2})".format(worksheet_name, column, rank)

def largest_value_name(worksheet_name, val_column, name_column, rank):
    return "=INDEX('{0}'!{2}:{2},MATCH(LARGE('{0}'!{1}:{1},{3}),'{0}'!{1}:{1},0))".format(worksheet_name, val_column, name_column, rank)
