import urllib3
from sudoku.sudoku import Sudoku

""" Op http://lipas.uwasa.fi/~timan/sudoku/ (Sudoku research page) 46 (difficulty rating 1 t/m 15, variant a,b en c 
en de AI Escarcor) Sudoku's. Deze worden gedownload en allemaal pgelost.
"""

urls = ['http://lipas.uwasa.fi/~timan/sudoku/s'+str(x).zfill(2)+y+".txt" for x in range(1,16) for y in ['a','b','c']]
urls.append("http://lipas.uwasa.fi/~timan/sudoku/s16.txt") # Dit is AI Escarcot


def convertSudokuToList(sudoku_string):
    """Converteert de Sudoku's naar het juiste formaat (list of lists)"""
    sudoku_lst = list()
    row_strings =  sudoku_string.split('\n')
    for row_string in row_strings:
        row_string = row_string.split(' ')
        if(len(row_string)>=9):
            sudoku_lst.append([int(x) for x in row_string if x != ''])
    return sudoku_lst

"""Download de Sudoku's en los ze op"""
http = urllib3.PoolManager()
for url in urls:
    r = http.request('GET', url)
    s = Sudoku(convertSudokuToList(r.data.decode('utf-8')))
    s.solve()
