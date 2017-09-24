from transform import produce_feature, grouped_fossil_records
from matcher import FullTextMatcher

def sample_row(holding, amount):
    return {'Sub-category/Classification':'Equity',
            'Local Authority': 'My pension fund',
            'Description of Holding': holding,
            'Amount': amount }

def category_row(string_match):
    return {'Match':string_match}

def test_something():
    matcher = FullTextMatcher()
    council_rows = [
        sample_row('McDonalds', '10.0'),
        sample_row('Blackrock', '30.0'),
        sample_row('Shell', '25.0'),
        sample_row('OilyMcOilFace', '15.0'),
        sample_row('CoalyMcCoalFace', '20.0'),
        sample_row('OilyMcOilFace', '13.0'),
        sample_row('ToysRUs', '1000.0'),
        sample_row('GassyCorp', '12.0')
    ]
    metadata = ['Shell','Blackrock','OilyMcOilFace', 'CoalyMcCoalFace', 'GassyCorp']
    out = produce_feature(matcher, council_rows, metadata, 'https://example.com/my.google.doc.url', 'My local authority')
    expected = {
        'post_title': 'My local authority',
        'post_content': '',
        'fund_name': 'My pension fund',
        'fund_value': 1125.0,
        'investment_value': 115.0,
        'google_doc_url': 'https://example.com/my.google.doc.url',
        'projected_indirect_investment':0,
        'direct_investment':115.0,
        'companies[0][\'name\']':'Blackrock',
        'companies[0][\'value\']':30.0,
        'companies[1][\'name\']':'OilyMcOilFace',
        'companies[1][\'value\']':28.0,
        'companies[2][\'name\']':'Shell',
        'companies[2][\'value\']':25.0,
        'companies[3][\'name\']':'CoalyMcCoalFace',
        'companies[3][\'value\']':20.0,
        'companies[4][\'name\']':'GassyCorp',
        'companies[4][\'value\']':12.0
    }
    assert out == expected

def test_grouping_fossil_records():
    rows = [
        sample_row('A', '10.0'),
        sample_row('B', '15.0'),
        sample_row('A', '13.0')
    ]
    expected = [ {'name':'A', 'value':23.0}
                ,{'name':'B', 'value':15.0}]
    assert grouped_fossil_records(rows) == expected
