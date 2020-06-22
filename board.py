import numpy as np
from sgfmill import sgf

class Game:
	def __init__(self, komi, board):
		self.board = board
		self.komi = komi
		self.board_sz = len(board)
		self.sgf_game = sgf.Sgf_game(size=len(board))

		# keeps track of board history for 'ko' rule
		self.board_hist = [np.copy(board)] 
	
		self.liberties = 0
		self.same_col_set = set([])
		# keeps track for scoring
		self.prisoners = {-1: 0, 1: 0}
		
	# method to return game tree
	def save_game(self, game_name):
		with open("./sgf_files/" + game_name + ".sgf", "wb") as f:
			f.write(self.sgf_game.serialise())  


	# function called from is_valid
	# valid Moves must not be suicidal 
	def _not_suicidal(self, move):
		self._place_piece(move)

		# first check if move captures anything. If not, do logic for suicidal move
		captures_anything = False

		# check to see if it captures anything. If capturing something, move valid
		moves_ls = self._get_cardinal_directions(move)
		for elem in moves_ls:
			# check OPPOSITE COLOR liberties
			self._flood_fill_liberties(elem, flip(move[2]))
			if self.liberties == 0 and len(self.same_col_set) != 0:
				captures_anything = True	

			# reset flood_fill params
			self.same_col_set = set([])
			self.liberties = 0

		# The move captures nothing - now we check if is also suicidal 
		if captures_anything is False:
			# check CURRENT color liberties
			self._flood_fill_liberties((move[0], move[1]), move[2])

			# placing the piece gives 0 liberties. suicidal
			if self.liberties == 0:

				# reset flood_fill params
				self.same_col_set = set([])
				self.liberties = 0

				self.board = np.copy(self.board_hist[-1]) # reset the board
				# False - the move IS suicidal and Invalid
				return False
			else: # there are liberties still. not suicidal

				# reset flood_fill params
				self.same_col_set = set([])
				self.liberties = 0

				self.board = np.copy(self.board_hist[-1]) # reset the board
				return True
			
		# something is captured, so move is not suicidal	
		else: # captures_anything is True
			self.board = np.copy(self.board_hist[-1]) # reset the board
			return True

	# function called from is_valid
	# determines if the ko rule is in effect
	def _ko_rule_valid(self, move):
		self._place_piece(move)
		# copy the prisoner dictionary for re-use
		prisoner_dict = dict(self.prisoners)

		# must evaluate the move to see
		self._life_and_death(move)
		
		ko_valid = True
	
		# ko is impossible for first few moves
		if len(self.board_hist) < 4:
			ko_valid = True
		
		# check previous board positions for ko rule 
		elif np.array_equal(self.board_hist[-2], self.board):
			ko_valid = False
		
		self.prisoners = prisoner_dict # reset the prisoner count after test
		self.board = np.copy(self.board_hist[-1]) # reset the board
		return ko_valid
		
	# Greedy boolean evaluation to see if it is valid
	def _is_valid(self, move):
		if self.board[move[0], move[1]] == 0:
			if self._not_suicidal(move):
				if self._ko_rule_valid(move):
					return True
				else:
					return False
			else:
				return False
		else:
			return False

	'''
	The main recursive algorithm for flood_fill.
	Flood fill explores adjacent spaces in the board which are of a 
	similar color. Stores info in global variable as it recurses

	A recursive solution is used because the board size is very small (20x20),
	and performance is not an issue
	'''
	def _flood_fill_liberties(self, start, cap_color):

		row, col = start
		directions = self._get_cardinal_directions(start)

		# the same color: keep looking
		if self.board[row, col] == cap_color: 
			self.same_col_set.add((row, col)) # keep track of the pieces seen

			# look in four directions for more spaces
			for direction in directions: 
				# test if move is on the board grid or is already explored
				if (direction not in self.same_col_set):
					self._flood_fill_liberties(direction, cap_color)

		elif self.board[row, col] == 0: # there is a liberty - its blank
			self.liberties += 1
			return
		elif self.board[row, col] == flip(cap_color): # opposite color. no liberty
			return 
		else:
			raise ValueError

		return 
		
	# removes the pieces in the 'seen' list if it has no liberties: they're captured
	def _remove_stones(self):
		for coord in self.same_col_set:
			x = coord[0]
			y = coord[1]
			self.board[x,y] = 0
			
	# looks in four directions to return list of directions to check
	def _get_cardinal_directions(self, move):
		# check life and death for all for directions
		up = (move[0] - 1, move[1])
		down = (move[0] + 1, move[1])
		left = (move[0], move[1] - 1)
		right = (move[0], move[1] + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if in_board(elem, self.board_sz):
				valid_list.append(elem)

		return valid_list

	# Checks which pieces are alive and which are dead. Updates it
	def _life_and_death(self, move):
		captured_color = flip(move[2])

		# look in four directions of piece placed to check captures
		valid_list = self._get_cardinal_directions(move)
		
		# run each check in four directions using flood_fill algorithm
		for elem in valid_list:
			self._flood_fill_liberties(elem, captured_color)
			if self.liberties == 0:
				self._remove_stones()

				# updates prisoners count
				prisoners_num = len(self.same_col_set)
				if captured_color == -1:
					self.prisoners[-1] += prisoners_num
				elif captured_color == 1:
					self.prisoners[1] += prisoners_num
				else: 
					raise ValueError

			# reset liberties and same_col_set
			self.liberties = 0
			self.same_col_set = set([])

	# places the piece on the board
	def _place_piece(self, move):
		x = move[0]
		y = move[1]
		self.board[x,y] = move[2]

	def _translate_move(self, move):
		#print("unadjusted move")
		if move[2] == 1:
			color = 'w'
		elif move[2] == -1:
			color = 'b'
		else:
			print("ERROR")#some error
		
		x =  (self.board_sz - 1) - move[0] 
		y = move[1]
		move = (x, y, color) 
		#print("adjusted move")
		#print(move)
		
		return move
	
	# keeps track of the SGF Tree for outputting
	def _update_sgf_tree(self, move):
		node = self.sgf_game.extend_main_sequence()
		move = self._translate_move(move)
		print("move[0]", move[0])
		print("move[1]", move[1])
		print("move[2]", move[2])
	
		node.set_move(move[2], (move[0], move[1]))
		#if move_info.comment is not None:
		#	node.set("C", move_info.comment)


	# the main entry point into board logic and board updating
	def update(self, move):

		# Player 'passes' in move, move color is '0'
		if move[2] == 0:
			self.board_hist.append(np.copy(self.board))
			return True	
		
		# make sure move is valid before placing
		if self._is_valid(move):
			#print(move)
			self._place_piece(move)
			self._life_and_death(move)
			self.board_hist.append(np.copy(self.board))
			self._update_sgf_tree(move)
			#add move to a SGF tree
			#sgf_w

			return True
		else:
			return False

# Class function used to flip turns
def flip(turn):
	if turn is -1: 
		return 1				
	elif turn is 1:
		return -1
	else:
		raise ValueError

def in_board(elem, sz):
	if (elem[0] >= 0 and elem[0] < sz
		and elem[1] >= 0 and elem[1] < sz):
		return True
	else:
		return False
