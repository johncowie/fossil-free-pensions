from spreadsheet import Spreadsheet

spreadsheet = Spreadsheet('creds.json')

print(spreadsheet.get_records('JurassicTest'))

# {
#  "type": "Feature",
#  "properties": {
#    "name": "Barnet",
#    "content": "",
#    "fund_name": "London Borough of Barnet Pension Fund",
#    "fund_value": "818,333,571",
#    "investment_value": "51,312,295",
#    "percentage": "6.27",
#    "direct_investment": "7,136,168",
#    "direct_percentage": "0.87",
#    "projected_indirect_investment": "44,176,127.00",
#    "indirect_percentage": "5.39",
#    "currency": "gbp",
#    "companies": [
#      {
#        "name": "RWE",
#        "value": "1,588,752"
#      },
#      {
#        "name": "RWE Finance",
#        "value": "723,173"
#      },
#      {
#        "name": "Exxon",
#        "value": "600,482"
#      },
#      {
#        "name": "Gazprom",
#        "value": "392,569"
#      },
#      {
#        "name": "Chevron",
#        "value": "329,448"
#      }
#    ],
#   "download": "",
#    "google_doc_url": "https://docs.google.com/spreadsheets/d/1qSFFaafZWPxSjFWVBOKXWMKH28M_k_TyzMvALk_3cxE/edit?usp=drivesdk"
#  },
#  "geometry": {
#    "type": "Polygon",
#    "coordinates": [
#      [
#        [
#          -0.13051700592,
#          51.6078338623
#        ],
#        [
#          -0.162648007274,
#          51.5664176941
#        ],
#        [
#          -0.204728007317,
#          51.5515403748
#        ],
#        [
#          -0.266775012016,
#          51.6010551453
#        ],
#        [
#          -0.293592989445,
#          51.6384162903
#        ],
#        [
#          -0.173332005739,
#          51.6663818359
#        ]
#      ]
#    ]
#  }
#}
