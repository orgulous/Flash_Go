import numpy as np
import moves
import card
from sgfmill import sgf, sgf_moves, ascii_boards
from sgfmill import boards
import copy

# This class contains all the legal move logic for a turn move. 
class GameLogic:
	def __init__(self, board, board_hist, size):
	
		self.board = board
		self.board_hist = board_hist
		self.board_sz = size
		
		self.liberties = 0
		self.same_col_set = set([])
				
	'''
	The main recursive algorithm for flood_fill.
	Flood fill explores adjacent spaces in the board which are of a 
	similar color. Stores info in global variable as it recurses

	A recursive solution is used because the board size is very small (20x20),
	and performance is not an issue
	'''
	
	def _is_empty(self, s):
		if s == 'check':
			return True
		elif s == 'blank':
			return True
		else:
			try: 
				int(s)
				return True
			except ValueError:
				return False
	
	def _flood_fill_liberties(self, start, cap_color):

		row, col = start
		directions = self._get_cardinal_directions_ff(start)
		
		look_pt = self.board[row, col]

		# the same color: keep looking
		if look_pt.symbol == cap_color: 
			self.same_col_set.add((row, col)) # keep track of the pieces seen

			# look in four directions for more spaces
			for direction in directions: 
				# test if move is on the board grid or is already explored
				if (direction not in self.same_col_set):
					self._flood_fill_liberties(direction, cap_color)

		# there is a liberty - its blank
		elif self._is_empty(look_pt.symbol): 
			self.liberties += 1
			return
		# opposite color. no liberty
		elif look_pt.symbol == moves.flip(cap_color): 
			return 
		else:
			#print("other thing was found", look_pt.symbol)
			#return
			raise ValueError

		return 
		

	# places the Move (type GridSquare) on the board
	def _place_piece(self, grid_sq):
		self.board[grid_sq.np_x, grid_sq.np_y] = grid_sq
		

	# looks in four directions to return list of directions to check
	def _get_cardinal_directions(self, grid_sq):
		# check life and death for all for directions
		
		up = (grid_sq.np_x - 1, grid_sq.np_y)
		down = (grid_sq.np_x + 1, grid_sq.np_y)
		left = (grid_sq.np_x, grid_sq.np_y - 1)
		right = (grid_sq.np_x, grid_sq.np_y + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if self._in_board(elem, self.board_sz):
				valid_list.append(elem)

		return valid_list

	# SECOND ONE FOR FLOOD FILL. REFACTOR LATER
	def _get_cardinal_directions_ff(self, move):
		# check life and death for all for directions
		
		up = (move[0] - 1, move[1])
		down = (move[0] + 1, move[1])
		left = (move[0], move[1] - 1)
		right = (move[0], move[1] + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if self._in_board(elem, self.board_sz):
				valid_list.append(elem)

		return valid_list


	# function called from is_valid
	# valid Moves must not be suicidal 
	def _not_suicidal(self, grid_sq):

		self._place_piece(grid_sq)
		
		# first check if move captures anything. If not, do logic for suicidal move
		captures_anything = False

		# check to see if it captures anything. If capturing something, move valid
		
		grid_sq_ls = self._get_cardinal_directions(grid_sq)
		for elem in grid_sq_ls:
			# check OPPOSITE COLOR liberties
			self._flood_fill_liberties(elem, moves.flip(grid_sq.symbol))
			if self.liberties == 0 and len(self.same_col_set) != 0:
				captures_anything = True	

			# reset flood_fill params
			self.same_col_set = set([])
			self.liberties = 0

		# The move captures nothing - now we check if is also suicidal 
		if captures_anything is False:
			# check CURRENT color liberties
			self._flood_fill_liberties((grid_sq.np_x, grid_sq.np_y), grid_sq.symbol)

			# placing the piece gives 0 liberties. suicidal
			if self.liberties == 0:

				# reset flood_fill params
				self.same_col_set = set([])
				self.liberties = 0

				self.board = copy.deepcopy(self.board_hist[-1]) # reset the board
				# False - the move IS suicidal and Invalid
				return False
			else: # there are liberties still. not suicidal

				# reset flood_fill params
				self.same_col_set = set([])
				self.liberties = 0

				self.board = copy.deepcopy(self.board_hist[-1]) # reset the board
				return True
			
		# something is captured, so move is not suicidal	
		else: # captures_anything is True
			self.board = copy.deepcopy(self.board_hist[-1]) # reset the board
			# PROBLEM. RESETING THE BOARD THIS WAY DOESN'T WORK BECAUSE ALL THE OBJECTS INSIDE ARE STILL REFERENCED
			return True
	# removes the pieces in the 'seen' list if it has no liberties: they're captured
	def _remove_stones(self):
		
		for coord in self.same_col_set:
			#print("removing stones")
			
			x = coord[0]
			y = coord[1]

			self.board[x,y].remove_stone()

			
	# Checks which pieces are alive and which are dead. Updates it
	def _life_and_death(self, grid_sq):
		captured_color = moves.flip(grid_sq.symbol)

		# look in four directions of piece placed to check captures
		valid_list = self._get_cardinal_directions(grid_sq)
		
		# run each check in four directions using flood_fill algorithm
		for elem in valid_list:
			self._flood_fill_liberties(elem, captured_color)
			
			if self.liberties == 0:
				self._remove_stones()

			# reset liberties and same_col_set
			self.liberties = 0
			self.same_col_set = set([])

	# why is this outside by itself? TODO
	def _in_board(self, elem, sz):
		if (elem[0] >= 0 and elem[0] < sz
			and elem[1] >= 0 and elem[1] < sz):
			return True
		else:
			return False

	# Get rid of soon
	def _board_equality(self):
		#np_equality = np.equal(,  dtype=np.object)
		equal_bool = True
		for x in range (self.board_sz):
			for y in range (self.board_sz):
				b0 = self.board_hist[-2]
				b1 = self.board
				if not b0[x,y].symbol == b1[x,y].symbol:
					equal_bool = False
		
		return equal_bool
		
	def run_move(self, grid_sq):
		self._place_piece(grid_sq)
		self._life_and_death(grid_sq)
		return self.board
				
	# function called from is_valid
	# determines if the ko rule is in effect
	def _ko_rule_apply(self, grid_sq):
		self._place_piece(grid_sq)
		
		# must evaluate the move to see
		print("Evaluating life and death for ko validity")
		self._life_and_death(grid_sq)
				
		ko_apply = False
		
		# ko is impossible for first few moves
		if len(self.board_hist) < 4:
			ko_apply = False

		# check previous board positions for ko rule 
		elif self._board_equality():
			#reset the board
			ko_apply = True
		
		self.board = copy.deepcopy(self.board_hist[-1]) #
		return ko_apply

	# Greedy boolean evaluation to see if it is valid
	def is_valid(self, grid_sq, board):
		
		# Extract where the place where you clicked to see 
		# if anything is there
		# Game should initialize a np array of empty grid points
		clicked_sq = board[grid_sq.np_x, grid_sq.np_y]
 
		if clicked_sq.is_blnk():
			print("its blank")
			if self._not_suicidal(grid_sq):
				print("its not suicidal")
				if self._ko_rule_apply(grid_sq) == False:
					print("its not a ko")
					return True
				else:
					print("It's a Ko. Invalid move")
					return False
			else:
				return False
		else:
			return False

	