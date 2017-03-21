from spreadsheet import local_authority, amount, holding
from schemas import validate_output

def fund_amounts(records):
    return map(amount, records)

def fund_value(records):
    return sum(fund_amounts(records))

def is_fossil_fuel_investment(record, metadata_rows):
    return holding(record) in metadata_rows

def fossil_records(records, metadata):
    return filter(lambda x: is_fossil_fuel_investment(x, metadata), records)

def fossil_value(records, metadata):
    return sum(fund_amounts(fossil_records(records, metadata)))

def produce_feature(la_data, metadata, google_doc_url, local_authority_name):
    direct_investment = fossil_value(la_data, metadata)
    output =  {
        'post_title': local_authority_name,
        'post_content': '',
        'fund_name': local_authority(la_data[0]),
        'fund_value': fund_value(la_data),
        'investment_value': fossil_value(la_data, metadata),
        'google_doc_url': google_doc_url,
        'projected_indirect_investment':0,
        'direct_investment': direct_investment
    }
    return validate_output(output)
