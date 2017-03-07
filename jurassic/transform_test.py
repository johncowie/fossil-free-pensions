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
    ]
    metadata = ['Shell','Blackrock']
    out = produce_feature(council_rows, metadata, 'https://example.com/my.google.doc.url', 'My local authority')
    expected = {
        'post_title': 'My local authority',
        'post_content': '',
        'fund_name': 'My pension fund',
        'fund_value': 65.0,
        'investment_value': 55.0,
        'google_doc_url': 'https://example.com/my.google.doc.url',
    }
    assert out == expected
