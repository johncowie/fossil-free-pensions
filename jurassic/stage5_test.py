import formula
import stage5

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
    expected = [ ['Name of Local Authority Pension Fund', 'Description of Holding', 'Sub-category/Classification', 'Oil/Gas Companies', 'Coal Companies', 'Verification', 'Fossil Fuel Amounts', 'All Amounts']
                ,['A fund', 'BP Oil', 'category1', formula.pattern_match('B2', oil_patterns), formula.pattern_match('B2', coal_patterns), formula.verification(2, 'D', 'E', 'B'), formula.fossil_amount(2, 'F', 'H'), '23400']
                ,['A fund', 'Big Coal', 'category2', formula.pattern_match('B3', oil_patterns), formula.pattern_match('B3', coal_patterns), formula.verification(3, 'D', 'E', 'B'), formula.fossil_amount(3, 'F', 'H'), '345.3']
                ,['A fund', 'Evil Doers', 'category3', formula.pattern_match('B4', oil_patterns), formula.pattern_match('B4', coal_patterns), formula.verification(4, 'D', 'E', 'B'), formula.fossil_amount(4, 'F', 'H'),'455.4']
                ]
    assert expected == stage5.full_data_tab('A fund', init_data, oil_patterns, coal_patterns)

def test_all_tabs():
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2')]
    oil_patterns = [('BP', '^BP*')]
    coal_patterns = [('King Coal', '^king coal')]
    expected = {'Full Data':stage5.full_data_tab('A fund', init_data, oil_patterns, coal_patterns)}
    assert stage5.gen_spreadsheet('A fund', init_data, oil_patterns, coal_patterns) == expected

def test_all_spreadsheets():
    pension_fund1 = [(fund_record('BP Oil', '1000', 'c1')),
                     (fund_record('Big Coal', '345.3', 'c2'))]
    pension_fund2 = [(fund_record('Gazprom', '2000', 'c1'))
                    ,(fund_record('Coca-cola', '3000', 'c2'))]
    pension_fund3 = [(fund_record('BP Oil', '2000', 'c1'))]
    oil_patterns = [('BP Oil', '^BP'), ('Gazprom', 'gazprom-regex')]
    coal_patterns = [('Big Coal', 'coal_pattern')]
    init_data = {'PF1': pension_fund1, 'PF2': pension_fund2, 'PF3': pension_fund3}
    expected_sheets = {'PF1':stage5.gen_spreadsheet('PF1', pension_fund1, oil_patterns, coal_patterns)
                      ,'PF2':stage5.gen_spreadsheet('PF2', pension_fund2, oil_patterns, coal_patterns)
                      ,'PF3':stage5.gen_spreadsheet('PF3', pension_fund3, oil_patterns, coal_patterns)}
    expected_meta = {'Investments': ['BP Oil', 'Big Coal', 'Coca-cola', 'Gazprom']}
    expected_meta = [['Holding', 'Oil Match', 'Coal Match']
                    ,['BP Oil', formula.pattern_match('A2', oil_patterns), formula.pattern_match('A2', coal_patterns)]
                    ,['Big Coal', formula.pattern_match('A3', oil_patterns), formula.pattern_match('A3', coal_patterns)]
                    ,['Coca-cola', formula.pattern_match('A4', oil_patterns), formula.pattern_match('A4', coal_patterns)]
                    ,['Gazprom', formula.pattern_match('A5', oil_patterns), formula.pattern_match('A5', coal_patterns)]]
    expected = {'sheets':expected_sheets, 'metadata':expected_meta}
    assert stage5.all_spreadsheets(init_data, oil_patterns, coal_patterns) == expected
