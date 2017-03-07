from schema import Schema, And, Use, Optional

_output_schema = Schema({
     'type': 'Feature'
    ,'properties': {
         'fund_name': str
        ,'fund_value': Use(float)
        ,'currency': 'gbp'
        ,'investment_value': Use(float)
    }
})

def validate_output(data):
    return _output_schema.validate(data)


