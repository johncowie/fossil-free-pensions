from spreadsheet import local_authority, amount, holding
from schemas import validate_output

def fund_amounts(records):
    return map(amount, records)

def fund_value(records):
    return sum(fund_amounts(records))

def is_fossil_fuel_investment(record, metadata_rows):
    return holding(record) in metadata_rows

def fossil_value(records, metadata):
    fossil_records = filter(lambda x: is_fossil_fuel_investment(x, metadata), records)
    return sum(fund_amounts(fossil_records))

def produce_feature(la_data, metadata, google_doc_url, local_authority_name):
    output =  {
        'post_title': local_authority_name,
        'post_content': '',
        'fund_name': local_authority(la_data[0]),
        'fund_value': fund_value(la_data),
        'investment_value': fossil_value(la_data, metadata),
        'google_doc_url': google_doc_url,
    }
    return validate_output(output)


