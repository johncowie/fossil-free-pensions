from spreadsheet import Spreadsheet
from transform import produce_feature
from matcher import FullTextMatcher
import json, os, csv

spreadsheet = Spreadsheet('creds.json')
matcher = FullTextMatcher()

records = spreadsheet.get_records('JurassicTest')
companies = list(map(lambda x: x['Oil/Gas'], spreadsheet.get_records('JurassicCategories')))


print(records)
print(companies)



data = produce_feature(matcher, records, companies, 'https://example.com', 'Local Authority')

class OurCSVDialect(csv.Dialect):
    delimiter = ','
    lineterminator = '\n'
    doublequote = True
    quoting = csv.QUOTE_ALL
    quotechar = '"'

with open('output_csv/test_output.csv', 'w') as csvfile:
    fieldnames = data.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=OurCSVDialect)

    writer.writeheader()
    writer.writerow(data)
