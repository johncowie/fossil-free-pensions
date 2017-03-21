from spreadsheet import local_authority, amount, holding
from schemas import validate_output
import itertools

def fund_amounts(records):
    return map(amount, records)

def fund_value(records):
    return sum(fund_amounts(records))

def is_fossil_fuel_investment(record, metadata_rows):
    return holding(record) in metadata_rows

def fossil_records(records, metadata):
    return filter(lambda x: is_fossil_fuel_investment(x, metadata), records)

# takes a list of records, groups by name (summing the value), and sorts by value
def grouped_fossil_records(records):
    groups = []
    data = sorted(records, key=holding)
    for k, g in itertools.groupby(data, holding):
        groups.append({'name': k, 'value':fund_value(g)})
    return sorted(groups, key=lambda x: x['value'], reverse=True)

def fossil_value(records, metadata):
    return sum(fund_amounts(fossil_records(records, metadata)))

def produce_feature(la_data, metadata, google_doc_url, local_authority_name):
    direct_investment = fossil_value(la_data, metadata)
    sorted_investments = grouped_fossil_records(fossil_records(la_data, metadata))
    output =  {
        'post_title': local_authority_name,
        'post_content': '',
        'fund_name': local_authority(la_data[0]),
        'fund_value': fund_value(la_data),
        'investment_value': fossil_value(la_data, metadata),
        'google_doc_url': google_doc_url,
        'projected_indirect_investment':0,
        'direct_investment': direct_investment,
        'companies[0][\'name\']':sorted_investments[0]['name'],
        'companies[0][\'value\']':sorted_investments[0]['value'],
        'companies[1][\'name\']':sorted_investments[1]['name'],
        'companies[1][\'value\']':sorted_investments[1]['value'],
        'companies[2][\'name\']':sorted_investments[2]['name'],
        'companies[2][\'value\']':sorted_investments[2]['value'],
        'companies[3][\'name\']':sorted_investments[3]['name'],
        'companies[3][\'value\']':sorted_investments[3]['value'],
        'companies[4][\'name\']':sorted_investments[4]['name'],
        'companies[4][\'value\']':sorted_investments[4]['value'],
    }
    return validate_output(output)
