import formula
import stage5
from spreadsheet import percentage, number_cell

def fund_record(investment_name, amount, category):
    return {'Description of Holding':investment_name,
            'Amount':amount,
            'Sub-category/Classification':category}

def test_pooled_data_tab():
    pool_matches = [{'Name':'ABC', 'Is Pooled? (Y/N)': 'Y'}
                   ,{'Name':'DEF', 'Is Pooled? (Y/N)': 'N'}]
    expected = [['Pooled fund estimate', percentage(0.1)]
               ,[None, 'Amount', 'Percentage', 'Name', 'Pooled fund', 'Estimated fossil fuel holdings', 'in % of total holdings']
               ,[]
               ,['Total', "='Fossil Fuel Direct Investments'!B2"]
               ,[1, formula.largest_value('Full Data', 'H', 1), "=B5/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 1), formula.pooled_match('D5:D19', pool_matches), '=IF(E5="yes",B5*$B$1,0)', '=F5/$B$4']
               ,[2, formula.largest_value('Full Data', 'H', 2), "=B6/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 2), None, '=IF(E6="yes",B6*$B$1,0)', '=F6/$B$4']
               ,[3, formula.largest_value('Full Data', 'H', 3), "=B7/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 3), None, '=IF(E7="yes",B7*$B$1,0)', '=F7/$B$4']
               ,[4, formula.largest_value('Full Data', 'H', 4), "=B8/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 4), None, '=IF(E8="yes",B8*$B$1,0)', '=F8/$B$4']
               ,[5, formula.largest_value('Full Data', 'H', 5), "=B9/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 5), None, '=IF(E9="yes",B9*$B$1,0)', '=F9/$B$4']
               ,[6, formula.largest_value('Full Data', 'H', 6), "=B10/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 6), None, '=IF(E10="yes",B10*$B$1,0)', '=F10/$B$4']
               ,[7, formula.largest_value('Full Data', 'H', 7), "=B11/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 7), None, '=IF(E11="yes",B11*$B$1,0)', '=F11/$B$4']
               ,[8, formula.largest_value('Full Data', 'H', 8), "=B12/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 8), None, '=IF(E12="yes",B12*$B$1,0)', '=F12/$B$4']
               ,[9, formula.largest_value('Full Data', 'H', 9), "=B13/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 9), None, '=IF(E13="yes",B13*$B$1,0)', '=F13/$B$4']
               ,[10, formula.largest_value('Full Data', 'H', 10), "=B14/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 10), None, '=IF(E14="yes",B14*$B$1,0)', '=F14/$B$4']
               ,[11, formula.largest_value('Full Data', 'H', 11), "=B15/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 11), None, '=IF(E15="yes",B15*$B$1,0)', '=F15/$B$4']
               ,[12, formula.largest_value('Full Data', 'H', 12), "=B16/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 12), None, '=IF(E16="yes",B16*$B$1,0)', '=F16/$B$4']
               ,[13, formula.largest_value('Full Data', 'H', 13), "=B17/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 13), None, '=IF(E17="yes",B17*$B$1,0)', '=F17/$B$4']
               ,[14, formula.largest_value('Full Data', 'H', 14), "=B18/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 14), None, '=IF(E18="yes",B18*$B$1,0)', '=F18/$B$4']
               ,[15, formula.largest_value('Full Data', 'H', 15), "=B19/$B$4", formula.largest_value_name('Full Data', 'H', 'B', 15), None, '=IF(E19="yes",B19*$B$1,0)', '=F19/$B$4']
               ,[None, None, None, None, 'Total estimated fossil fuels in largest pooled funds', '=SUM(F5:F19)', '=SUM(G5:G19)']
               ,[None, None, None, None, 'Total direct fossil fuels', "='Fossil Fuel Direct Investments'!B3", "='Fossil Fuel Direct Investments'!B4"]
               ,[]
               ,[None, None, None, None, 'Total fossil fuels', '=F20+F21', '=G20+G21']
               ,[None, None, None, None, 'Total holdings', "='Fossil Fuel Direct Investments'!B2"]
               ]
    assert expected == stage5.pooled_data_tab(pool_matches, 20)

def test_full_data_tab():
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2'),
                 fund_record('Evil Doers', '455.4', 'category3')]
    oil_patterns = [{'name':'BP', 'pattern':'^BP*'},
                    {'name':'Shell', 'pattern':'shell'}]
    coal_patterns = [{'name':'King Coal', 'pattern':'^king coal'}]
    expected = [ ['Name of Local Authority Pension Fund', 'Description of Holding', 'Sub-category/Classification', 'Oil/Gas Companies', 'Coal Companies', 'Verification', 'Fossil Fuel Amounts', 'All Amounts']
                ,['A fund', 'BP Oil', 'category1', formula.pattern_match('B2:B', oil_patterns), formula.pattern_match('B2:B', coal_patterns), formula.verification(2, 'D', 'E', 'B'), formula.fossil_amount(2, 'F', 'H'), number_cell(23400.0)]
                ,['A fund', 'Big Coal', 'category2', None, None, formula.verification(3, 'D', 'E', 'B'), formula.fossil_amount(3, 'F', 'H'), number_cell(345.3)]
                ,['A fund', 'Evil Doers', 'category3', None, None, formula.verification(4, 'D', 'E', 'B'), formula.fossil_amount(4, 'F', 'H'),number_cell(455.4)]
                ]
    assert expected == stage5.full_data_tab('A fund', init_data, oil_patterns, coal_patterns)

def test_fracking_full_data_tab():
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2'),
                 fund_record('Evil Doers', '455.4', 'category3')]
    fracking_patterns = [{'name':'BP', 'pattern':'^BP*'},
                         {'name':'Shell', 'pattern':'shell'}]
    expected = [ ['Name of Local Authority Pension Fund', 'Description of Holding', 'Sub-category/Classification', 'Fracking Companies',  'Verification', 'Fossil Fuel Amounts', 'All Amounts']
                ,['A fund', 'BP Oil', 'category1', formula.pattern_match('B2:B', fracking_patterns), formula.verification_1col(2, 'D', 'B'), formula.fossil_amount(2, 'E', 'G'), number_cell(23400.0)]
                ,['A fund', 'Big Coal', 'category2', None, formula.verification_1col(3, 'D', 'B'), formula.fossil_amount(3, 'E', 'G'), number_cell(345.3)]
                ,['A fund', 'Evil Doers', 'category3', None, formula.verification_1col(4, 'D', 'B'), formula.fossil_amount(4, 'E', 'G'),number_cell(455.4)]
                ]
    assert expected == stage5.fracking_full_data_tab('A fund', init_data, fracking_patterns)
    
def test_direct_investments_tab():
    expected = [ ['Name', "='Full Data'!A2"]
                ,['Total holdings', "=SUM('Full Data'!H1:H)"]
                ,['Total fossil fuel holdings', "=SUM('Full Data'!G2:G)"]
                ,['Percentage in fossil fuels', percentage("=B3/B2")]
                ,[]
                ,[]
                ,['Top 10 Fossil Fuel Holdings', '', '', '', 'This excludes holdings through pooled funds - see next sheet']
                ,['Amount', 'Percentage', 'Name']
                ,[formula.largest_value('Full Data', 'G', 1), percentage("=A9/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 1)]
                ,[formula.largest_value('Full Data', 'G', 2), percentage("=A10/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 2)]
                ,[formula.largest_value('Full Data', 'G', 3), percentage("=A11/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 3)]
                ,[formula.largest_value('Full Data', 'G', 4), percentage("=A12/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 4)]
                ,[formula.largest_value('Full Data', 'G', 5), percentage("=A13/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 5)]
                ,[formula.largest_value('Full Data', 'G', 6), percentage("=A14/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 6)]
                ,[formula.largest_value('Full Data', 'G', 7), percentage("=A15/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 7)]
                ,[formula.largest_value('Full Data', 'G', 8), percentage("=A16/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 8)]
                ,[formula.largest_value('Full Data', 'G', 9), percentage("=A17/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 9)]
                ,[formula.largest_value('Full Data', 'G', 10), percentage("=A18/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 10)]
                ]
    assert stage5.direct_investments_tab() == expected

def test_all_tabs():
    init_data = {'data': [fund_record('BP Oil', '23400', 'category1'),
                          fund_record('Big Coal', '345.3', 'category2')]
                 ,'pooled': [{'Is Pooled? (Y/N)':'yes', 'Name':'BP Oil'}]
                 }
    oil_patterns = [{'name':'BP', 'pattern':'^BP*'}]
    coal_patterns = [{'name':'King Coal', 'pattern':'^king coal'}]
    expected = [ ('Full Data', stage5.full_data_tab('A fund', init_data['data'], oil_patterns, coal_patterns))
               , ('Fossil Fuel Direct Investments', stage5.direct_investments_tab())
               , ('Pooled Funds & Total Fossil Fuels', stage5.pooled_data_tab(init_data['pooled'], 2))
               , ('Overview figures', stage5.overview_tab())]
    assert stage5.gen_spreadsheet('A fund', init_data, oil_patterns, coal_patterns) == expected

# FIXME sort out this test
def xtest_all_spreadsheets():
    pension_fund1 = [(fund_record('BP Oil', '1000', 'c1')),
                     (fund_record('Big Coal', '345.3', 'c2'))]
    pension_fund2 = [(fund_record('Gazprom', '2000', 'c1'))
                    ,(fund_record('Coca-cola', '3000', 'c2'))]
    pension_fund3 = [(fund_record('BP Oil', '2000', 'c1'))]
    oil_patterns = [{'name':'BP Oil', 'pattern':'^BP'}, {'name':'Gazprom', 'pattern':'gazprom-regex'}]
    coal_patterns = [{'name':'Big Coal', 'pattern':'coal_pattern'}]
    init_data = {'PF1': pension_fund1, 'PF2': pension_fund2, 'PF3': pension_fund3}
    expected_sheets = {'PF1':stage5.gen_spreadsheet('PF1', pension_fund1, oil_patterns, coal_patterns)
                      ,'PF2':stage5.gen_spreadsheet('PF2', pension_fund2, oil_patterns, coal_patterns)
                      ,'PF3':stage5.gen_spreadsheet('PF3', pension_fund3, oil_patterns, coal_patterns)}
    expected_meta = {'Investments': ['BP Oil', 'Big Coal', 'Coca-cola', 'Gazprom']}
    expected_meta = [['Holding', 'Oil Match', 'Coal Match']
                    ,['BP Oil', formula.pattern_match('A2:A', oil_patterns), formula.pattern_match('A2:A', coal_patterns)]
                    ,['Big Coal', None, None]
                    ,['Coca-cola', None, None]
                    ,['Gazprom', None, None]]
    expected = {'sheets':expected_sheets, 'metadata':{'METADATA-MATCHES':{'Matches':expected_meta}}}
    assert stage5.all_spreadsheets(init_data, oil_patterns, coal_patterns) == expected

def test_include_file():
    assert stage5.include_file('ABC', None, ['ABC']) == False
    assert stage5.include_file('ABC', None, None) == True
    assert stage5.include_file('ABC', ['DEF'], None) == False
