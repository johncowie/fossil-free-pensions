from functools import reduce

def flatten_grid(grid):
    max_width = reduce(max, map(len, grid))
    flattened = []
    for row in grid:
        flattened = flattened + row + (max_width - len(row)) * ['']
    return flattened
