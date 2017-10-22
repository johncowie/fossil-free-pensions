from spreadsheet import string_cell, formula_cell, percentage, cells_request, number_cell

def test_format_cells():
    grid = [ ["a", percentage("0/3")]
            ,["b", "=1/2", 2, 4.4] ]
    sheet_id = 37
    expected = {
        'updateCells':{
            'rows':[ {'values':[string_cell("a"), percentage("0/3")]}
                    ,{'values':[string_cell("b"), formula_cell("=1/2"), number_cell(2), number_cell(4.4)]}]
           ,'fields':'*'
           ,'start':{'sheetId':sheet_id, 'rowIndex':0, 'columnIndex':0}
         }
    }
    assert cells_request(sheet_id, grid) == expected

def test_number_cell():
    assert number_cell('3.3') == number_cell(3.3)
    assert number_cell('3,333.0') == number_cell(3333.0)
