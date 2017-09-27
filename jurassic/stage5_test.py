import formula
from stage5 import full_data_tab

def fund_record(investment_name, amount, category):
    return {'Description of Holding':investment_name,
            'Amount':amount,
            'Sub-category/Classification':category}

def test_full_data_tab():
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2'),
                 fund_record('Evil Doers', '455.4', 'category3')]
    oil_patterns = [('BP', '^BP*'),
                    ('Shell', 'shell')]
    coal_patterns = [('King Coal', '^king coal')]
    expected = [ ['Name of Local Authority Pension Fund', 'Description of Holding', 'Sub-category/Classification', 'Oil/Gas Companies', 'Coal Companies', 'Verification', 'All Amounts']
                ,['A fund', 'BP Oil', 'category1', formula.pattern_match('B2', oil_patterns), formula.pattern_match('B2', coal_patterns), formula.verification(2, 'D', 'E', 'B'), '23400']
                ,['A fund', 'Big Coal', 'category2', formula.pattern_match('B3', oil_patterns), formula.pattern_match('B3', coal_patterns), formula.verification(3, 'D', 'E', 'B'), '345.3']
                ,['A fund', 'Evil Doers', 'category3', formula.pattern_match('B4', oil_patterns), formula.pattern_match('B4', coal_patterns), formula.verification(4, 'D', 'E', 'B'), '455.4']
                ]
    assert expected == full_data_tab('A fund', init_data, oil_patterns, coal_patterns)
