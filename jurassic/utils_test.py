import utils

def test_normalise_grid():
    input = [['A1', 'B1', 'C1', 'D1'],
             ['A2', 'B2', 'C2'],
             [],
             ['A4', 'B4', 'C4']]
    expected = [['A1', 'B1', 'C1', 'D1']
               ,['A2', 'B2', 'C2', '']
               ,['',    '',  '',   '']
               ,['A4', 'B4', 'C4', '']]
    assert utils.normalise_grid(input) == expected

def test_flatten_grid():
    input = [['A1', 'B1', 'C1', 'D1'],
             ['A2', 'B2', 'C2',  ''],
             ['',    '',  '',   ''],
             ['A4', 'B4', 'C4', '']]
    expected = ['A1', 'B1', 'C1', 'D1'
               ,'A2', 'B2', 'C2', ''
               ,'',    '',  '',   ''
               ,'A4', 'B4', 'C4', '']
    assert utils.flatten(input) == expected

def test_i_to_2d():
    assert utils.i_to_2d(0, 3) == (0, 0)
    assert utils.i_to_2d(1, 3) == (1, 0)
    assert utils.i_to_2d(2, 3) == (2, 0)
    assert utils.i_to_2d(3, 3) == (0, 1)
    assert utils.i_to_2d(4, 3) == (1, 1)
    assert utils.i_to_2d(33, 10) == (3, 3)
