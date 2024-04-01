import sys; args = sys.argv[1:]
from time import perf_counter
STATS={}
#TIMES=[]
def updateStats(keyPhrase):
    if keyPhrase not in STATS:
        STATS[keyPhrase]=1
    else:
        STATS[keyPhrase]+=1
def getSymset(puzzle, neighbors, maxLength):
    #start = perf_counter()
    updateStats("getSymset is called")
    lstOfPeriods = []
    mostconstrained = ''
    for cs in constraint_sets:
        for sym in symbols:
            symbolPeriodLst = [i for i in cs if sym not in neighbors[i] and puzzle[i] == '.']
            if len(symbolPeriodLst)>0 and (len(lstOfPeriods)==0 or len(lstOfPeriods)>len(symbolPeriodLst)):
                lstOfPeriods = symbolPeriodLst
                mostconstrained = sym
            if len(lstOfPeriods)==1:
                #end = perf_counter()
                #TIMES.append(end-start)
                return [[idx, mostconstrained] for idx in lstOfPeriods]
                
    if maxLength>len(lstOfPeriods):
        #end = perf_counter()
        #TIMES.append(end-start)
        return [[idx, mostconstrained] for idx in lstOfPeriods]
    #end = perf_counter()
    #TIMES.append(end-start)
    return []
def get_constraints(index, board_size):
    row = index // board_size
    column = index % board_size
    box_size = int(board_size ** 0.5)
    box_row = row // box_size
    box_col = column // box_size
    constraints1 = set()
    constraints2 = set()
    constraints3 = set()
    for col in range(board_size):
        constraints1.add(row * board_size + col)
    for r in range(board_size):
        constraints2.add(r * board_size + column)
    start_row = box_row * box_size
    start_col = box_col * box_size
    for r in range(start_row, start_row + box_size):
        for c in range(start_col, start_col + box_size):
            constraints3.add(r * board_size + c)
    return [constraints1,constraints2,constraints3]
def setGlobals(pzl):
    global neighborList
    neighborList = []
    for i in range(len(pzl)):
        nbrs1 = get_constraints(i,9)
        nbrs = nbrs1[0].union(nbrs1[1]).union(nbrs1[2])   
        neighborList.append(nbrs)
def make_set_of_constraints(n):
    set_of_constraints = [set() for _ in range(3 * n)]
    for i in range(n):
        for j in range(n):
            cell_num = i * n + j
            set_of_constraints[i].add(cell_num)
            set_of_constraints[n + j].add(cell_num)
            subbox_size = int(n ** 0.5)  
            subbox_num = (i // subbox_size) * subbox_size + (j // subbox_size)  
            set_of_constraints[2 * n + subbox_num].add(cell_num)
    return set_of_constraints
def checkSum(pzl, symbols):
    minimum = min([ord(i) for i in symbols])
    sumVariable = 0
    for i in pzl:
        sumVariable += ord(i)-minimum
    return sumVariable
def bruteForce(puzzle, symbolsOfNBRS):
    updateStats("bruteforce called")
    if not "." in puzzle: return puzzle
    period = [i for i in range(len(puzzle)) if puzzle[i] == '.']
    minimum = None
    for i in period:
        tupl = (len(symbols) - len(symbolsOfNBRS[i]), i)
        if tupl[0] < 2:
            minimum = tupl
            break
        elif minimum and minimum > tupl or not minimum:
            minimum = tupl
    choices = [[minimum[1], j] for j in symbols if j not in symbolsOfNBRS[minimum[1]]]
    updateStats(f"choice ct {len(choices)}")
    if len(choices) >= 2:
        temporary = getSymset(puzzle, symbolsOfNBRS, len(choices))
        choices = temporary if temporary else choices
    for choice in choices:
        new_puzzle = list(puzzle)
        new_puzzle[choice[0]] = choice[1]
        new_puzzle = ''.join(new_puzzle)
        newVals = {}
        if len(choices) != 1:
            newVals = {k : {*symbolsOfNBRS[k]} for k in symbolsOfNBRS}
        else:
            newVals = symbolsOfNBRS
        for a in nbrs[choice[0]]:
            newVals[a].add(choice[1])
        bF = bruteForce(new_puzzle, newVals)
        if bF: return bF
    return ""
puzzles = []
count = 0
start1 = perf_counter()
puzzles = open(args[0]).read().splitlines()
for puzzle in puzzles:
    count += 1
    start = perf_counter()
    theDimensions = int(len(puzzle)**0.5)
    height = 0
    width = 0
    symbols = [str(i) for i in range(1, 10)]
    lookup_table = {i : [] for i in range(len(puzzle))}
    nbrs = {}
    nbrvals = {}
    countStatLookupTable = 0
    for i in range((int(theDimensions**0.5)), 0, -1):
        if theDimensions % i == 0:
            x = theDimensions / i
            width = int(max(x, i))
            height = int(min(x, i))
            break
    if theDimensions == 12:
        symbols += ['A','B','C']
    elif theDimensions == 4:
        symbols = {'1','2','3','4'}
    elif theDimensions == 6:
        symbols = {'1','2','3','4','5','6'}
    elif "D" in puzzle or "F" in puzzle or "Z" in puzzle or "Y" in puzzle or "W" in puzzle or "U" in puzzle or "N" in puzzle:
        symbols = set()
        for i in puzzle:
            symbols.add(i)
        symbols.remove(".")
        if len(symbols)==8:
            symbols.add("S")
    rows = [[j for j in range(i, i + theDimensions)] for i in range(0, len(puzzle), theDimensions)]
    cols = [[j for j in range(i, len(puzzle), theDimensions)] for i in range(theDimensions)]
    blocks = []
    for i in range(0, theDimensions, height):
        for j in range(0, theDimensions, width):
            temp = []
            for k in range(i, i + height):
                for l in range(j, j + width):
                    temp.append(k * theDimensions + l)
            blocks.append(temp)     
    constraint_sets = rows+cols+blocks
    for i in constraint_sets:
        for j in i:
            lookup_table[j].append(countStatLookupTable)
        countStatLookupTable += 1
    for i in range(len(puzzle)):
        nbrs[i] = set(constraint_sets[lookup_table[i][0]]).union(set(constraint_sets[lookup_table[i][1]]),set(constraint_sets[lookup_table[i][2]]))
        nbrs[i].remove(i)
        nbrvals[i] = {puzzle[x] for x in nbrs[i] if puzzle[x] != '.'} 
    bF = bruteForce(puzzle, nbrvals)
    checksum = checkSum(bF,symbols)
    if not bF:
        bF = puzzle
    end = perf_counter()
    # if count < 10:
    #     print(str(count) + ': ' + puzzle)
    #     print("   " + bF, checksum, str(end-start) + 's')
    # elif count < 100:
    #     print(str(count) + ': ' + puzzle)
    #     print("    " + bF, checksum, str(end-start) + 's')
    # else:
    #     print(str(count) + ': ' + puzzle)
    #     print("     " + bF, checksum, str(end-start) + 's')
SIZE = int(len(bF)**(1/2))
for i in range(SIZE):
        for j in range(SIZE):
            print(bF[i * SIZE + j], end=" ")
        print()

end1 = perf_counter()
# print(end1-start1)

# print("STATS - ", STATS)




#Aarav Gupta, period 4, 2025