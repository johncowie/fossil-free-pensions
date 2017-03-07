from schema import Schema, And, Use, Optional

_output_schema = Schema({
    'post_title': str,
    'post_content': str,
    'fund_name': str,
    'fund_value': Use(float),
    'investment_value': Use(float),
    'google_doc_url': str,
})

def validate_output(data):
    return _output_schema.validate(data)


