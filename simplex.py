class SimplexRow:

	def __init__(self, rowType, rowValues):
		self.__rowID = rowType
		self.__rowValues = rowValues
		self.__rowOperation = ""
		self.__divResult = -1
		self.__rowIterationCount = 0

	def __getitem__(self, i):
		if i >= 0 and i<len(self.__rowValues):
			return self.__rowValues[i]
		return 1

	def __len__(self):
		return len(self.__rowValues)

	def getRHS(self):
		return self.__rowValues[len(self.__rowValues)-1]

	def getRowID(self):
		return self.__rowID + str(self.__rowIterationCount)

	def printRow(self):
		printString = self.getRowID() + " |"
		for i in range(0, len(self.__rowValues)):
			printString += str(self.__rowValues[i]) + " |"
		printString += self.__rowOperation
		print(printString)

	def getdivResult(self, collumn):
		try:
			self.__divResult = self.getRHS()/self.__rowValues[collumn]
		except:
			self.__divResult = -1
		return self.__divResult

	def doPivotRowCalculation(self, pivotCollumn):
		divider = self.__rowValues[pivotCollumn]
		self.__rowOperation = self.getRowID() + '/' + str(divider)
		for i in range(0, len(self.__rowValues)):
			self.__rowValues[i] /= divider
		self.__rowIterationCount += 1

	def iterateRow(self, pivotCollumn, pivotRow):
		pivotRowMultiplier = self.__rowValues[pivotCollumn] / pivotRow[pivotCollumn]
		pivotRowMultiplier *= -1
		self.__rowOperation = self.getRowID() + str(pivotRowMultiplier) + pivotRow.getRowID()
		for i in range(0, len(self.__rowValues)):
			self.__rowValues[i] = self.__rowValues[i] + (pivotRowMultiplier * pivotRow[i])
		self.__rowIterationCount += 1

class Tableau:

	def __init__(self, collumnHeaders, matrix):
		self.__pivotRow = 1
		self.__pivotCollumn = 1
		self.__headers = collumnHeaders
		self.__table = [SimplexRow("O", matrix[0])]
		currentRowValue = 'a'
		for i in range(1,len(matrix)):
			self.__table.append(SimplexRow(currentRowValue, matrix[i]))
			currentRowValue = chr(ord(currentRowValue)+1)

	def __determineIfComplete(self):
		for i in range(0,len(self.__table[0])):
			if self.__table[0][i] < 0:
				return False
		return True

	def __findPivotColumn(self):
		minValue = 0
		self.__pivotCollumn = 1
		for i in range(0,len(self.__table)):
			if self.__table[0][i] < 0:
				if self.__table[0][i] < minValue:
					minValue = self.__table[0][i]
					self.__pivotCollumn = i

	def __findPivotRow(self):
		divResult = 1000000.0
		self.__pivotRow = 1
		for i in range(0, len(self.__table)):
			tempResult = self.__table[i].getdivResult(self.__pivotCollumn)
			if tempResult > 0:
				if tempResult < divResult:
					divResult = tempResult
					self.__pivotRow = i

	def __iterateTableau(self):
		if not self.__determineIfComplete():
			self.__findPivotColumn()
			self.__findPivotRow()
			self.__table[self.__pivotRow].doPivotRowCalculation(self.__pivotCollumn)
			for i in range (0, len(self.__table)):
				if i != self.__pivotRow:
					self.__table[i].iterateRow(self.__pivotCollumn, self.__table[self.__pivotRow])

	def solveTableau(self):
		self.printTableau()
		while not self.__determineIfComplete():
			self.__iterateTableau()
			self.printTableau()

		for i in range(0, len(self.__headers)-2):
			nonZeroCount = 0
			oneCount = 0
			onePosition = 0
			for j in range(0, len(self.__table)):
				cacheValue = self.__table[j][i]
				if cacheValue == 1:
					oneCount += 1
					onePosition = j
				elif cacheValue != 0:
					nonZeroCount += 1
			if nonZeroCount == 0 and oneCount == 1:
				print(self.__headers[i],"has a value of",self.__table[onePosition].getRHS())
			else:
				print(self.__headers[i],"has no value")

	def printTableau(self):
		print()
		printString = "    ";
		for i in range(0, len(self.__headers)):
			printString += str(self.__headers[i]) + " |"
		print(printString)
		for i in range(0, len(self.__table)):
			self.__table[i].printRow()


def main():
	table = Tableau(['P','a','b','c','s','t','u','v','RHS','OPERATION'],[[1,-8,-7,-4,0,0,0,0,0],
		[0,10,8,5,1,0,0,0,400],
		[0,0,2,5,0,1,0,0,70],
		[0,2,4,1,0,0,1,0,176],
		[0,5,1,3,0,0,0,1,80]])

	table.solveTableau()

	tableTwo = Tableau(['P','x','y','z','s','t','RHS','OPERATION'],[
		[1,-120,-180,-250,0,0,0],
		[0,4,5,10,1,0,120],
		[0,30,50,80,0,1,1000]])
	tableTwo.solveTableau()

if __name__ == '__main__':
	main()