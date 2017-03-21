from schema import Schema, And, Use, Optional

_output_schema = Schema({
    'post_title': str,
    'post_content': str,
    'fund_name': str,
    'fund_value': Use(float),
    'investment_value': Use(float),
    'google_doc_url': str,
    'projected_indirect_investment':Use(float),
    'direct_investment': Use(float),
    'companies[0][\'name\']':str,
    'companies[0][\'value\']':Use(float),
    'companies[1][\'name\']':str,
    'companies[1][\'value\']':Use(float),
    'companies[2][\'name\']':str,
    'companies[2][\'value\']':Use(float),
    'companies[3][\'name\']':str,
    'companies[3][\'value\']':Use(float),
    'companies[4][\'name\']':str,
    'companies[4][\'value\']':Use(float),

})

def validate_output(data):
    return _output_schema.validate(data)
