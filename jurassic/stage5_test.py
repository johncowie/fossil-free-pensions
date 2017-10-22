import formula
import stage5
from spreadsheet import percentage, number_cell

def fund_record(investment_name, amount, category):
    return {'Description of Holding':investment_name,
            'Amount':amount,
            'Sub-category/Classification':category}

def test_full_data_tab():
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2'),
                 fund_record('Evil Doers', '455.4', 'category3')]
    oil_patterns = [{'name':'BP', 'pattern':'^BP*'},
                    {'name':'Shell', 'pattern':'shell'}]
    coal_patterns = [{'name':'King Coal', 'pattern':'^king coal'}]
    expected = [ ['Name of Local Authority Pension Fund', 'Description of Holding', 'Sub-category/Classification', 'Oil/Gas Companies', 'Coal Companies', 'Verification', 'Fossil Fuel Amounts', 'All Amounts']
                ,['A fund', 'BP Oil', 'category1', formula.pattern_match('B2:B', oil_patterns), formula.pattern_match('B2:B', coal_patterns), formula.verification(2, 'D', 'E', 'B'), formula.fossil_amount(2, 'F', 'H'), number_cell(23400.0)]
                ,['A fund', 'Big Coal', 'category2', "", "", formula.verification(3, 'D', 'E', 'B'), formula.fossil_amount(3, 'F', 'H'), number_cell(345.3)]
                ,['A fund', 'Evil Doers', 'category3', "", "", formula.verification(4, 'D', 'E', 'B'), formula.fossil_amount(4, 'F', 'H'),number_cell(455.4)]
                ]
    assert expected == stage5.full_data_tab('A fund', init_data, oil_patterns, coal_patterns)

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
    init_data = [fund_record('BP Oil', '23400', 'category1'),
                 fund_record('Big Coal', '345.3', 'category2')]
    oil_patterns = [{'name':'BP', 'pattern':'^BP*'}]
    coal_patterns = [{'name':'King Coal', 'pattern':'^king coal'}]
    expected = {'Full Data':stage5.full_data_tab('A fund', init_data, oil_patterns, coal_patterns)
                ,'Fossil Fuel Direct Investments':stage5.direct_investments_tab()}
    assert stage5.gen_spreadsheet('A fund', init_data, oil_patterns, coal_patterns) == expected

def test_all_spreadsheets():
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
                    ,['BP Oil', formula.pattern_match('A2', oil_patterns), formula.pattern_match('A2', coal_patterns)]
                    ,['Big Coal', formula.pattern_match('A3', oil_patterns), formula.pattern_match('A3', coal_patterns)]
                    ,['Coca-cola', formula.pattern_match('A4', oil_patterns), formula.pattern_match('A4', coal_patterns)]
                    ,['Gazprom', formula.pattern_match('A5', oil_patterns), formula.pattern_match('A5', coal_patterns)]]
    expected = {'sheets':expected_sheets, 'metadata':{'METADATA-MATCHES':{'Matches':expected_meta}}}
    assert stage5.all_spreadsheets(init_data, oil_patterns, coal_patterns) == expected
