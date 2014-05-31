

## This is a helper class that is used by _Carts
class Gridder():
	
	def __init__(self, maxRow, maxCol):
		self.maxR = maxRow
		self.maxC = maxCol
		
		pass
	
	def MakeCoord(self, ROW, COL):
		return (str)(ROW)+"x"+(str)(COL)
	
	def ValidCoord(self, ROW, COL):
		if ROW <= self.maxR and COL <= self.maxC:
			return True
		else: 
			return False
	
	
	def GenRadius(self, ROW, COL, dirR, dirC):
		### ROW COL
		## dirXY is 0 if it moves negatively in that axial direction from the pivot point
		## maxX x maxY should be a valid location
		arr = []
	
		## change columns (x-axis)
		if dirC is 1:
			col = 1
			while col < COL:
				if self.ValidCoord(ROW, col):
					arr.append( self.MakeCoord(ROW, col))
				col += 1
		elif dirC is 0:
			col = self.maxC
			while col > COL:
				if self.ValidCoord(ROW, col):
					arr.append( self.MakeCoord(ROW, col))
				col -= 1
	
	
	
		## change rows (y-axis)
		if dirR is 1:
			row = ROW + 1
			while row <= self.maxR:
				if self.ValidCoord(row, COL):
					arr.append( self.MakeCoord(row, COL))
				row += 1
		elif dirR is 0:
			row = ROW - 1
			while row > 0:
				if self.ValidCoord(row, COL):
					arr.append( self.MakeCoord(row, COL))
				row -= 1
	
		## pivot point
		if self.ValidCoord(ROW, COL):
			arr.append( self.MakeCoord(ROW,COL) )
	
	
		return arr
	

	## rowcol is a tuple (row, col)
	def GridCorner(self, rowcol): 
		ROW = rowcol[0]
		COL = rowcol[1]
		
		## X Y should be starting coordinates
		Add = lambda x,y: x+y
		Sub = lambda x,y: x-y
	
		rOp = Add
		dirR = 0
		if ROW == self.maxR: 
			dirR = 1
			rOp = Sub
	
		cOp = Add
		dirC = 1
		if COL == self.maxC: 
			dirC = 0
			cOp = Sub
	
		arr = []
		while 0 < ROW <= self.maxR or 0 < COL <= self.maxC: ### and
			#print MakeCoord(ROW, COL)
			arr.extend( self.GenRadius(ROW, COL, dirR, dirC) )
			ROW = rOp(ROW, 1)
			COL = cOp(COL, 1)
		
		return arr


#print GridCorner(1,1, 6,6)
#print GridCorner(1,6, 6,6)
#print GridCorner(6,1, 6,6)	
#print GridCorner(6,6, 6,6)
	