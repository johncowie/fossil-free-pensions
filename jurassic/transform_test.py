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
         sample_row('Alternative', 'McDonalds', '10.0')
        ,sample_row('Equity', 'Blackrock', '30.0')
        ,sample_row('Alternative', 'Shell', '25.0')
    ]
    metadata = ['Shell','Blackrock']
    out = produce_feature(council_rows, metadata)
    expected = {
        'type': 'Feature'
        ,'properties':{
             'fund_name': 'My pension fund'
            ,'fund_value': 65.0
            ,'investment_value': 55.0
            ,'currency': 'gbp'
        }
    }
    assert out == expected
