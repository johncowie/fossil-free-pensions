from transform import produce_feature

def sample_row(category, holding, amount):
    return {'Sub-category/Classification':category,
            'Local Authority': 'My pension fund',
            'Description of Holding': holding,
            'Amount': amount }

def category_row(string_match):
    return {'Match':string_match}

def test_something():
    council_rows = [
        sample_row('Alternative', 'McDonalds', '10.0'),
        sample_row('Equity', 'Blackrock', '30.0'),
        sample_row('Alternative', 'Shell', '25.0'),
        sample_row('Alternative', 'OilyMcOilFace', '15.0'),
        sample_row('Equity', 'CoalyMcCoalFace', '20.0'),
        sample_row('Equity', 'OilyMcOilFace', '13.0'),
        sample_row('Alternative', 'ToysRUs', '1000.0'),
        sample_row('Equity', 'GassyCorp', '12.0')
    ]
    metadata = ['Shell','Blackrock','OilyMcOilFace', 'CoalyMcCoalFace', 'GassyCorp']
    out = produce_feature(council_rows, metadata, 'https://example.com/my.google.doc.url', 'My local authority')
    expected = {
        'post_title': 'My local authority',
        'post_content': '',
        'fund_name': 'My pension fund',
        'fund_value': 1125.0,
        'investment_value': 115.0,
        'google_doc_url': 'https://example.com/my.google.doc.url',
        'projected_indirect_investment':0,
        'direct_investment':115.0,
        # 'companies[0][\'name\']':'Blackrock',
        # 'companies[0][\'value\']':30.0,
        # 'companies[1][\'name\']':'OilyMcOilFace',
        # 'companies[1][\'value\']':28.0,
        # 'companies[2][\'name\']':'Shell',
        # 'companies[2][\'value\']':25.0,
        # 'companies[3][\'name\']':'CoalyMcCoalFace',
        # 'companies[3][\'value\']':20.0,
        # 'companies[4][\'name\']':'GassyCorp',
        # 'companies[4][\'value\']':12.0
    }
    assert out == expected
