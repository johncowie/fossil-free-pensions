import utils

def test_flatten_grid():
    input = [['A1', 'B1', 'C1', 'D1'],
             ['A2', 'B2', 'C2'],
             [],
             ['A4', 'B4', 'C4']]
    expected = ['A1', 'B1', 'C1', 'D1'
               ,'A2', 'B2', 'C2', ''
               ,'',    '',  '',   ''
               ,'A4', 'B4', 'C4', '']
    assert utils.flatten_grid(input) == expected
