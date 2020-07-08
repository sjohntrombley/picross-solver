from enum import Enum, auto

class Cell(Enum):
    unknown = auto()
    filled = auto()
    empty = auto()

    def __str__(self):
        return ('█' if self is Cell.filled else
                'X' if self is Cell.empty else
                '?'
                )

def clue_sanity_check(r_clues, c_clues):
    # Type Checks
    if type(r_clues) is not list:
        raise TypeError('r_clues must be a list.')
    if type(c_clues) is not list:
        raise TypeError('c_clues must be a list.')
    if any(type(clue) is not list for clue in r_clues):
        raise TypeError('r_clues must be a list of lists.')
    if any(type(clue) is not list for clue in c_clues):
        raise TypeError('c_clues must be a list of lists.')
    if any(any(type(n) is not int for n in clue) for clue in r_clues):
        raise TypeError('All elements of r_clues must contain only ints.')
    if any(any(type(n) is not int for n in clue) for clue in c_clues):
        raise TypeError('All elements of c_clues must contain only ints.')
    # Check for clues that are too long
    if any(sum(clue)+len(clue)-1 > len(c_clues) for clue in r_clues):
        raise ValueError(
                'One of the clues in r_clues is too big for this puzzle.'
                )
    if any(sum(clue)+len(clue)-1 > len(r_clues) for clue in c_clues):
        raise ValueError(
                'One of the clues in c_clues is too big for this puzzle.'
                )

class Puzzle:
    def __init__(self, r_clues, c_clues):
        clue_sanity_check(r_clues, c_clues)
        self.row_clues = r_clues
        self.column_clues = c_clues

class Row(list):
    def __init__(self, n_cols):
        super().__init__()
        super().extend(Cell.unknown for _ in range(n_cols))

    def __setitem__(self, key, value):
        if type(value) is not Cell:
            raise ValueError('Elements of a Row must be Cells.')
        super().__setitem__(key, value)

    def __str__(self):
        return ''.join(str(cell) for cell in self)

    __delitem__ = None
    __iadd__ = None
    __imul__ = None
    append = None
    clear = None
    extend = None
    insert = None
    pop = None
    remove = None
    reverse = None
    sort = None

class Grid(list):
    def __init__(self, n_rows, n_cols):
        super().__init__()
        super().extend(Row(n_cols) for _ in range(n_rows))

    def __setitem__(self, key, value):
        if type(value) is not Row:
            raise TypeError('Elements of a Grid must be Rows.')
        if len(value) != len(self[key]):
            raise ValueError('Cannot change the size of Rows in a Grid.')
        super().__setitem__(key, value)

    def __str__(self):
        return '\n'.join(str(row) for row in self)

    __delitem__ = None
    __iadd__ = None
    __imul__ = None
    append = None
    clear = None
    extend = None
    insert = None
    pop = None
    remove = None
    reverse = None
    sort = None

def is_last_gap(gap):
    return gap[-1]==0 and all(g==1 for g in gap[1:-1])

def next_gap(gap):
    if is_last_gap(gap):
        return gap
    if gap[-1] > 0:
        return gap[:-2] + [ gap[-2]+1, gap[-1]-1 ]
    for i in reversed(range(len(gap)-1)):
        if gap[i] > 1:
            return (
                    gap[:i-1] +
                    [gap[i-1]+1] +
                    [1]*(len(gap)-i-1) +
                    [sum(gap[i:])+i-len(gap)]
                    )

def gaps_gen(clues, length):
    gap = [0] + [1]*(len(clues)-1) + [length-sum(clues)-len(clues)+1]
    yield gap
    while not is_last_gap(gap):
        gap = next_gap(gap)
        yield gap

def merge_gaps(clues, updates, gap):
    # Skip this arrangement if impossible
    if any(
            cell['locked'] and cell['state'] is Cell.filled
            for cell in updates[:gap[0]]
            ):
        return
    offset = gap[0]
    for i in range(len(clues)):
        if any(
                cell['locked'] and cell['state'] is Cell.empty
                for cell in updates[offset:offset+clues[i]]
                ):
            return
        offset += clues[i]
        if any(
                cell['locked'] and cell['state'] is Cell.filled
                for cell in updates[offset:offset+gap[i+1]]
                ):
            return
        offset += gap[i+1]

    # Merge the current arrangement
    for cell_index in range(gap[0]):
        if not updates[cell_index]['locked']:
            if updates[cell_index]['state'] is Cell.unknown:
                updates[cell_index]['state'] = Cell.empty
            elif updates[cell_index]['state'] is Cell.filled:
                updates[cell_index]['locked'] = True
                updates[cell_index]['state'] = Cell.unknown
    offset = gap[0]
    for clue_index in range(len(clues)):
        for cell_index in range(offset,offset+clues[clue_index]):
            if not updates[cell_index]['locked']:
                if updates[cell_index]['state'] is Cell.unknown:
                    updates[cell_index]['state'] = Cell.filled
                elif updates[cell_index]['state'] is Cell.empty:
                    updates[cell_index]['locked'] = True
                    updates[cell_index]['state'] = Cell.unknown
        offset += clues[clue_index]

        for cell_index in range(offset,offset+gap[clue_index+1]):
            if not updates[cell_index]['locked']:
                if updates[cell_index]['state'] is Cell.unknown:
                    updates[cell_index]['state'] = Cell.empty
                elif updates[cell_index]['state'] is Cell.filled:
                    updates[cell_index]['locked'] = True
                    updates[cell_index]['state'] = Cell.unknown
        offset += gap[clue_index+1]

def solve2(p):
    if type(p) is not Puzzle:
        raise TypeError("First argument to solve2 must be of Puzzle type.")
    grid = Grid(len(p.row_clues), len(p.column_clues))
    row_clues, col_clues = p.row_clues, p.column_clues
    update, done = True, False
    #pass_n = 1
    #print(grid)
    #input('Do row pass?')
    while update and not done:
        update, done = False, True
        # Row pass
        for row_index,this_row_clues in enumerate(row_clues):
            this_row = grid[row_index]
            # Go to next row if this row is done
            if all(state is not Cell.unknown for state in this_row):
                continue

            this_row_clues = row_clues[row_index]
            # Check for empty rows
            if len(this_row_clues)==0:
                grid[row_index] = [Cell.empty]*len(this_row)
                update = True
                continue

            this_row_updates = [ {'state':state, 'locked':state is not Cell.unknown} for state in this_row ]
            # Loop through possible arrangements
            for gap in gaps_gen(this_row_clues, len(this_row)):
                merge_gaps(this_row_clues, this_row_updates, gap)

            # Update the grid
            for col_index, cell in enumerate(this_row_updates):
                if cell['locked'] and cell['state'] is Cell.unknown:
                    done = False
                elif not cell['locked'] and cell['state'] is not Cell.unknown:
                    grid[row_index][col_index] = cell['state']
                    update = True
        if done:
            break
        done = True
        #print(f'pass: {pass_n}')
        #print(grid)
        #input('Do col pass?')

        # Column pass
        for col_index,this_col_clues in enumerate(col_clues):
            #print(f'==> col_index: {col_index}')
            #print(f'==> this_col_clues: {this_col_clues}')
            this_col = [ row[col_index] for row in grid ]
            #print(f'==> this_col: {pretty_slice(this_col)}')

            # Go to next col if this col is done
            if all(state is not Cell.unknown for state in this_col):
                continue

            # Check for empty rows
            if len(this_col_clues)==0:
                for row_index in range(len(this_col)):
                    grid[row_index][col_index] = Cell.empty
                update = True
                continue

            this_col_updates = [ {'state':state, 'locked':state is not Cell.unknown} for state in this_col ]
            #print(f'==> [before]this_col_updates: {pretty_update(this_col_updates)}')
            # Loop through possible arrangements
            for gap in gaps_gen(this_col_clues, len(this_col)):
                merge_gaps(this_col_clues, this_col_updates, gap)
            #print(f'==> [after]this_col_updates: {pretty_update(this_col_updates)}')

            # Update the grid
            #print(f'{this_col}\n{this_col_updates}')
            for row_index, cell in enumerate(this_col_updates):
                if cell['locked'] and cell['state'] is Cell.unknown:
                    done = False
                elif not cell['locked'] and cell['state'] is not Cell.unknown:
                    #print(f'{row_index} {col_index}')
                    grid[row_index][col_index] = cell['state']
                    update = True
        #print(grid)
        #input('Do row pass?')
    return grid

#def main():
#    row_clues = ''
#    while row_clues == '':
#        row_clues = input('Enter row clues: ').strip()
#        if row_clues[0]!='[' or row_clues[-1]!=']':
#            row_clues = ''
#            continue
#        row_clues

def main():
    n_rows, n_cols = 0, 0
    while n_rows==0:
        dimension_string = input("Enter puzzle dimensions: ")
        dimensions = dimension_string.lower().split('x')
        if len(dimensions)==2:
            try:
                n_rows = int(dimensions[0])
                n_cols = int(dimensions[1])
            except ValueError:
                n_row, n_cols = 0, 0
                print('Error: Invalid dimensions. Dimensions should be input in the form rxc where are is the number of rows and c is the number of columns')
        else:
            print('Error: Invalid dimensions. Dimensions should be input in the form rxc where are is the number of rows and c is the number of columns')

    row_clues = []
    for row_index in range(n_rows):
        valid_clue = False
        while not valid_clue:
            try:
                row_clues.append([int(clue) for clue in input(f'Enter clues for row {row_index+1}: ').split(' ')])
                valid_clue = True
            except ValueError:
                print('Error: Invalid clue. Clues should be a list of positive integers separated by spaces.')

    col_clues = []
    for col_index in range(n_cols):
        valid_clue = False
        while not valid_clue:
            try:
                col_clues.append([int(clue) for clue in input(f'Enter clues for col {col_index+1}: ').split(' ')])
                valid_clue = True
            except ValueError:
                print('Error: Invalid clue. Clues should be a list of positive integers separated by spaces.')
    p = Puzzle(row_clues, col_clues)
    print(solve2(p))

if __name__ == "__main__":
    main()

#def solve(p):
#    if type(p) is not Puzzle:
#        raise TypeError(type(p))
#    grid = Grid(p.row_clues, p.column_clues)
#    row_clues, col_clues = p.row_clues, p.column_clues
#    update, done = True, False
#    while update and not done:
#        update, done = False, True
#        for i in range(len(row_clues)):
#            row = grid[i].copy()
#            if all(cell is not Cell.unknown for cell in row):
#                continue
#            if len(row_clues[i]) == 0:
#                grid[i] = [ Cell.empty for _ in row ]
#                update = True
#                continue
#            for j in range(len(row_clues[i])):
#                clue_min = 0
#                for clue in row_clues[i][:j]:
#                    while (
#                        clue_min+clue+row_clues[i][j] < len(row)
#                        and (
#                            any(cell is Cell.empty for cell in row[clue_min:clue_min+clue])
#                            or row[clue_min+clue] is Cell.filled
#                            )
#                        ):
#                        clue_min += 1
#                    if clue_min+clue+row_clues[i][j] == len(row):
#                        raise f'Impossible! row: {i} clue: {j} grid:\n{grid}'
#                    clue_min += clue+1
#                clue_max = len(row) - 1
#                for clue in reversed(row_clues[i][j+1:]):
#                    while (
#                        clue_min+row_clues[i][j]+clue <= clue_max
#                        and (
#                            any(cell is Cell.empty for cell in row[clue_max-clue+1:clue_max+1])
#                            or row[clue_max-clue] is Cell.filled
#                            )
#                        ):
#                        clue_max -= 1
#                    if clue_min+row_clues[i][j]+clue > clue_max:
#                        raise f'Impossible! row: {i} clue: {j} grid:\n{grid}'
#                    clue_max -= clue+1
#                while clue_min+row_clues[i][j] <= clue_max+1 and row[clue_min] is Cell.empty:
#                    clue_min += 1
#                if clue_min+row_clues[i][j] > clue_max+1:
#                    raise f'Impossible! row: {i} clue: {j} grid:\n{grid}'
#                while clue_min+row_clues[i][j] <= clue_max+1 and row[clue_max] is Cell.empty:
#                    clue_max -= 1
#                if clue_min+row_clues[i][j] > clue_max+1:
#                    raise f'Impossible! row: {i} clue: {j} grid:\n{grid}'
#                if all(cell is not Cell.empty for cell in row[clue_min:clue_max+1]):
#                    if clue_max-clue_min+1 < 2*row_clues[i][j]:
#                        blank = clue_max-clue_min+1-row_clues[i][j]
#                        grid[i][clue_min+blank:clue_min+row_clues[i][j]] = [Cell.filled] * (row_clues[i][j]-blank)
#                        update = True
#                        row = grid[i].copy()
#                    continue
#                gaps = [0]
#                for cell in row[clue_min:clue_max+1]:
#                    if cell is cell.empty:
#                        if gaps[-1] != 0:
#                            gaps.append(0)
#                        continue
#                    gaps[-1] += 1
#                if all(gap < row_clues[i][j] for gap in gaps):
#                    raise f'Impossible! row: {i} clue: {j} grid:\n{grid}'
#                if len([gap for gap in gaps if gap >= row_clues[i][j]]) > 1:
#                    continue
#                while any(cell is Cell.empty for cell in row[clue_min:clue_min+row_clues[i][j]]):
#                    while row[clue_min] is not Cell.empty:
#                        clue_min += 1
#                    while row[clue_min] is Cell.empty:
#                        clue_min += 1
#                gap = [gap for gap in gaps if gap >= row_clues[i][j]][0]
#                if gap < 2*row_clues[i][j]:
#                    blank = gap - row_clues[i][j]
#                    grid[i][clue_min+blank:clue_min+row_clues[i][j]] = [Cell.filled] * (row_clues[i][j]-blank)
#                    update = True
#            # Check for new blanks and connections
