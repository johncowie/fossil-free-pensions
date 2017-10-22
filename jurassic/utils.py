from functools import reduce

def grid_rows(grid):
    return len(grid)

def grid_cols(grid):
    return reduce(max, map(len, grid))

def cell_range(rows, cols):
    col_letter = chr(65 + (cols-1))
    return 'A1:'+col_letter+str(rows)

def i_to_2d(i, width):
    return (i % width, i // width)

def normalise_grid(grid):
    max_width = reduce(max, map(len, grid))
    rows = []
    for row in grid:
        rows.append(row + (max_width - len(row)) * [''])
    return rows

def flatten(lists):
    flattened = []
    for l in lists:
        for val in l:
            flattened.append(val)
    return flattened
