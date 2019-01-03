import numpy as np

""" @package Sudoku
Deze package bevat een klasse om een Sudoku op te lossen. De oplossingsstrategieen zijn gabaseerd op:
https://www.sudoku-solutions.com/index.php?page=background
"""

class Sudoku:
    """
    In de Sudoku-class wordt de Sudoku grid opgeslagen en zijn alle functies opgenomen om de Sudoku op te lossen.
    Er zijn meerdere oplossingsstrategieen die achtereenvolgens worden ingezet om de Sudoku op te lossen. Als  de
    verschillende oplossingsstrategieen de Sudoku niet kunnen oplossen worden de resterende cijfers met d.m.v.
    bruteforce (backtracking) ingevuld
    """

    debug = False

    def __init__(self,grid,debug=False):
        """De constructor de de Sudoku grid in het juiste format op (9x9 numpy array)"""
        self.grid = np.array(grid)
        self.debug = debug

        # bgrid is een grid met daarin de 'candidattes'. Door eliminatie worden candidates uitgesloten
        self.bgrid = np.full((9, 9), 511, dtype=int) #b1 1111 1111 = 511
        self.bvalid = [2**x for x in range(0,9)] #Valid binary values, verplaatsen naar self.searchForNakedSingle?

        for r,c in self.iterateGrid():
            if self.grid[r,c] > 0:
                self.setValue(r,c,self.grid[r,c])


    def iterateGrid(self):
        """Grid iterator

        Deze functie retouneert 81-tuples met daarin de rij/kolom combinaties. Voorkomt iedere keer dubbele for-loop:
        for r in range(9):
            for c in range(9)
                return [(i,j) for i in range(9) for j in range(9)]
        """
        return [(i,j) for i in range(9) for j in range(9)]


    def setValue(self,r,c,v,msg=""):
        """Vul een waarde in op de de Sudoku

        r -- rij index
        c -- kolom index
        v -- waarde
        """
        self.eliminateCandidates(r,c,v)
        if self.debug:
            print ("Set ", chr(65+r) + str(c+1),'=',v,' (',r,',',c,')',msg, sep='')
        # Zet de waarde van de cel
        self.grid[r,c] = v
        self.bgrid[r,c] = 0 #2**(v-1)


    def isValidValue(self,r,c,v):
        """Controleert of de waarde (v) geldig is.

        De functie retouneert 'True' als de waarde niet voorkomt in dezelfde rij, kolom én box.
        """
        return any([v in self.grid[r,:], v in self.grid[:,c], v in self.getBox(r,c)])==False


    def eliminateCandidates(self,r,c,v):
        """Eliminieert candidate waarden"""
        # Verwijder waarde bij alle peers in dezelfde ...
        bInvValue = int(511 ^ 2**(v-1))  # Inverse van de binaire waarde van v
        self.bgrid[r,:] = np.bitwise_and(self.bgrid[r,:],bInvValue) #... rij        
        self.bgrid[:,c] = np.bitwise_and(self.bgrid[:,c],bInvValue) #... kolom

        #... 3x3 box
        topr,topc = self.getUpperLeftOfBox(r,c)
        self.bgrid[topr:topr+3, topc:topc+3] = np.bitwise_and(self.bgrid[topr:topr+3, topc:topc+3],bInvValue)


    def printGrid(self):
        """Print de sudoku op een nette manier"""
        for i,r in enumerate(self.grid):
            if i == 0:
                print('   ',' '.join(['1','2','3','|','4','5','6','|', '7','8','9']))
            if i % 3 == 0:
                print(" ","-"*25)

            for j,c in enumerate(r):
                if j == 0:
                    print(chr(65+i),end=" ")
                if j % 3 == 0:
                    print("|",end=" ")
                print(c,end=" ")
            print("|")

        print("-"*25)


    def isSolved(self):
        """Controleert de sudoku regels

        De waarde 1 t/m mag slechts één keer voorkomen een een rij, kolom of box. De som van deze waarden
        is 45. Als alles optelt tot 45 is de sudoku correct.
        """
        #Row sum
        rowsum = np.sum(self.grid,1)

        #col sum
        colsum = np.sum(self.grid,0)

        # 3x3 box csum
        boxsum = []
        for i in range(0,8,3):
            for j in range(0,8,3):
                boxsum.append(self.grid[i:i+3, j:j+3].sum())
        boxsum = np.array(boxsum)

        if all(rowsum==45) and all(colsum==45) and all(boxsum==45):
            return True
        return False


    def getBox(self,r,c):
        """Bepaal de box. Retouneert de box als een 3x3 array"""
        # Bepaal links boven van box
        topr,topc = self.getUpperLeftOfBox(r,c)

        return self.grid[topr:topr+3, topc:topc+3]


    def solve(self):
        """Wrapper die alle oplossingsstrategieen uitvoert"""
        made_replacement = True
        run = 0
        while made_replacement:
            run += 1
            if self.debug:
                print("Run", run)
            made_replacement = self.searchForNakedSingle()
            made_replacement = made_replacement or self.searchForHiddenSingles() 
            # Als je deze combineert met vorige regel dan wordt wordt het volgende uitgevoerd 
            # Run 1: searchForNakedSingle() --> replacement
            # Run 2: searchForNakedSingle() --> geen replacement (overbodig, want alle uniques zijn al ingevuld)
            # Run 2: searchForHiddenSingles()

        self.solveBruteForce()

        if self.isSolved():
            print("Sudoku opgelost!")
            #self.printGrid()
        else:
            print("Sudoku is niet opgelost. Ongeldige sudoku?")


    def searchForNakedSingle(self):
        """Bij een naked single blijft er door eliminatie nog meer één mogelijke waarde over."""
        made_replacement = False
        for r,c in self.iterateGrid():
            if self.grid[r,c]==0 and self.bgrid[r,c] in self.bvalid: # self.bvalid of len(convBinToDecList.c)==1?
                # De waarde is nog niet ingevuld (grid[rc]==0) en is een singleton (bgrid[r,c] in bvalid)
                made_replacement = True
                #self.setValue(r,c,2**(self.bgrid[r,c]-1))
                v = self.bvalid.index(self.bgrid[r,c])+1
                self.setValue(r,c,v)

        return made_replacement
    

    def searchForHiddenSingle(self, r, c, type="row"):
        """Als een cel door eliminatie meerdere waarden overhoudt, kan voor iedere mogelijk waarde gekeken of
        deze waarde nog ergens anders in de rij/kolom/box voor mag komen. Als de waarde niet op een andere plek
        mag voorkomen dan kan deze worden ingevuld in de geselecteerde cel.
        """
        validValues = self.getCandidateList(r,c)

        for y in validValues:
            if type=="row":
                peers = self.bgrid[r,:]
            elif type=="col":
                peers = self.bgrid[:,c]
            elif type=="box":
                topr,topc = self.getUpperLeftOfBox(r,c)
                peers = self.bgrid[topr:topr+3, topc:topc+3].ravel()

            peers = np.bitwise_and(peers, 2**(y-1))
            if sum([z>0 for z in peers]) == 1:
                self.setValue(r,c,y)
                return True

        return False
    

    def searchForHiddenSingles(self):
        """Wrapper voor searchForHiddenSingle. Itereert over iedere cel en zoekt naar een hidden single in respectievelijk
        de rij, kolom en box.
        """
        made_replacement = False
        k = 0
        for i,j in self.iterateGrid():
            k += 1
            if self.grid[i,j] != 0:
                continue    #Waarde al ingevuld
            x = self.getCandidateList(i,j)
            for y in x:
                if self.searchForHiddenSingle(i,j,"row"):
                    made_replacement = True
                    break
                
                if self.searchForHiddenSingle(i,j,"col"):
                    made_replacement = True
                    break

                if self.searchForHiddenSingle(i,j,"box"):
                    made_replacement = True
                    break

        return made_replacement


    def getUpperLeftOfBox(self,r,c):
        """Geef matrix indices van de linker boven hoek van de box"""
        return (r - r%3, c - c%3)


    def getCandidateList(self,r,c):
        """Bepaalt o.b.v. de sudoku grid welke waarden niet zijn geëlimineerd""" 
        return [x+1 for x in range(9) if np.bitwise_and(self.bgrid[r,c],2**x)]


    def getAllCandidates(self):
        """Bepaal welke candidates er zijn voor de cellen die nog niet ingevuld zijn"""
        missing_values = list()
        for r,c in self.iterateGrid():
            candidates = self.getCandidateList(r,c)
            if len(candidates) >= 1:
                missing_values.append((r,c,candidates)) # append zodat list blijft behouden (i.t.t. extend)
        
        return missing_values


    def solveBruteForce(self):
        """Oplossen m.b.v. bruteforce (backtracking)"""
        missing_values = self.getAllCandidates()

        z = 0 # Tijdelijke counter om aantal iteraties te limiteren
        idx = [0]*len(missing_values) # Welke index is gebruikt?

        i = 0
        while i < len(missing_values):
            assert i >= 0, "i out of range: "+str(i)
            r,c,v = missing_values[i]

            if idx[i]+1 > len(v):
                idx[i]=0
                self.grid[r,c]=0
                i-=1
                continue

            if self.isValidValue(r,c,v[idx[i]]):
                self.grid[r,c] = v[idx[i]]
                idx[i]+=1 
                i+=1
            else:
                idx[i]+=1
                self.grid[r,c] = 0

if __name__ == '__main__':
    s = Sudoku([[0,0,9,0,0,0,0,0,0],
            [3,0,0,0,0,0,0,6,7],
            [0,0,0,5,7,2,0,3,0],
            [0,8,0,0,0,7,5,0,0],
            [4,0,0,0,6,0,0,0,3],
            [0,0,5,8,0,0,0,1,0],
            [0,4,0,9,5,6,0,0,0],
            [9,6,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,3,0,0]],debug=True)

    s.solve()
