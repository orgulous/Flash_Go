import numpy as np
import moves
from sgfmill import sgf
from sgfmill import boards
import copy

class Game:
	def __init__(self, komi, board):
		self.board = board
		self.komi = komi
		self.board_sz = len(board)
		self.sgf_game = sgf.Sgf_game(size=len(board))

		# keeps track of board history for 'ko' rule
		self.board_hist = [copy.deepcopy(board)] 
		#self.working_state = None # tracking for new obj
	
		self.liberties = 0
		self.same_col_set = set([])
		
		# keeps track for scoring (unusued now)
		self.prisoners = {'b': 0, 'w': 0}
		
	# method to return game tree
	def save_game(self, game_name):
		with open("./sgf_files/" + game_name + ".sgf", "wb") as f:
			f.write(self.sgf_game.serialise())  
			
	#def open_game():
	#	with 

	'''
	The main recursive algorithm for flood_fill.
	Flood fill explores adjacent spaces in the board which are of a 
	similar color. Stores info in global variable as it recurses

	A recursive solution is used because the board size is very small (20x20),
	and performance is not an issue
	'''
	def _flood_fill_liberties(self, start, cap_color):

		row, col = start
		directions = self._get_cardinal_directions_ff(start)
		
		look_pt = self.board[row, col]

		# the same color: keep looking
		if look_pt.color == cap_color: 
			self.same_col_set.add((row, col)) # keep track of the pieces seen

			# look in four directions for more spaces
			for direction in directions: 
				# test if move is on the board grid or is already explored
				if (direction not in self.same_col_set):
					self._flood_fill_liberties(direction, cap_color)

		# there is a liberty - its blank
		elif look_pt.color == 'blnk': 
			self.liberties += 1
			return
		# opposite color. no liberty
		elif look_pt.color == moves.flip(cap_color): 
			return 
		else:
			raise ValueError

		return 
		

	# places the Move (type GridPoint) on the board
	def _place_piece(self, grid_pt):
		self.board[grid_pt.np_x, grid_pt.np_y] = grid_pt
		

	# looks in four directions to return list of directions to check
	def _get_cardinal_directions(self, grid_pt):
		# check life and death for all for directions
		
		up = (grid_pt.np_x - 1, grid_pt.np_y)
		down = (grid_pt.np_x + 1, grid_pt.np_y)
		left = (grid_pt.np_x, grid_pt.np_y - 1)
		right = (grid_pt.np_x, grid_pt.np_y + 1)

		# makes sure each move is valid
		raw_list = [up, down, left, right]
		valid_list = []
		for elem in raw_list:
			if in_board(elem, self.board_sz):
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
			if in_board(elem, self.board_sz):
				valid_list.append(elem)

		return valid_list


	# function called from is_valid
	# valid Moves must not be suicidal 
	def _not_suicidal(self, grid_pt):

		self._place_piece(grid_pt)
		
		# first check if move captures anything. If not, do logic for suicidal move
		captures_anything = False

		# check to see if it captures anything. If capturing something, move valid
		
		grid_pt_ls = self._get_cardinal_directions(grid_pt)
		for elem in grid_pt_ls:
			# check OPPOSITE COLOR liberties
			self._flood_fill_liberties(elem, moves.flip(grid_pt.color))
			if self.liberties == 0 and len(self.same_col_set) != 0:
				#print("Something is captured")
				captures_anything = True	

			# reset flood_fill params
			self.same_col_set = set([])
			self.liberties = 0

		# The move captures nothing - now we check if is also suicidal 
		if captures_anything is False:
			#print("Nothing is captured")
			# check CURRENT color liberties
			self._flood_fill_liberties((grid_pt.np_x, grid_pt.np_y), grid_pt.color)

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
	def _life_and_death(self, grid_pt):
		captured_color = moves.flip(grid_pt.color)

		# look in four directions of piece placed to check captures
		valid_list = self._get_cardinal_directions(grid_pt)
		
		# run each check in four directions using flood_fill algorithm
		for elem in valid_list:
			self._flood_fill_liberties(elem, captured_color)
			
			if self.liberties == 0:
				self._remove_stones()

				# updates prisoners count
				prisoners_num = len(self.same_col_set)
				if captured_color == 'b':
					self.prisoners['b'] += prisoners_num
				elif captured_color == 'w':
					self.prisoners['w'] += prisoners_num
				else: 
					raise ValueError

			# reset liberties and same_col_set
			self.liberties = 0
			self.same_col_set = set([])

	# Get rid of soon
	def _board_equality(self):
		#np_equality = np.equal(,  dtype=np.object)
		equal_bool = True
		for x in range (self.board_sz):
			for y in range (self.board_sz):
				b0 = self.board_hist[-2]
				b1 = self.board
				if not b0[x,y].color == b1[x,y].color:
					equal_bool = False
		
		return equal_bool
		
	# function called from is_valid
	# determines if the ko rule is in effect
	def _ko_rule_apply(self, grid_pt):
		self._place_piece(grid_pt)
		# copy the prisoner dictionary for re-use
		prisoner_dict = dict(self.prisoners)

		# must evaluate the move to see
		print("Evaluating life and death for ko validity")
		self._life_and_death(grid_pt)
				
		#Edit this part to speed it up later

		
		#self.prisoners = prisoner_dict # reset the prisoner count after test
		ko_apply = False
		
		# ko is impossible for first few moves
		if len(self.board_hist) < 4:
			ko_apply = False

		# check previous board positions for ko rule 
		# TODO object comparison np array
		#elif np.array_equal(self.board_hist[-2], self.board):
		elif self._board_equality():
			#reset the board
			ko_apply = True
		
		self.board = copy.deepcopy(self.board_hist[-1]) #
		return ko_apply



	# Greedy boolean evaluation to see if it is valid
	def _is_valid(self, grid_pt):
		
		# Extract where the place where you clicked to see 
		# if anything is there
		# Game should initialize a np array of empty grid points
		clicked_sq = self.board[grid_pt.np_x, grid_pt.np_y]
 
		if clicked_sq.is_blnk():
			print("its blank")
			if self._not_suicidal(grid_pt):
				print("its not suicidal")
				if self._ko_rule_apply(grid_pt) == False:
					print("its not a ko")
					return True
				else:
					print("It's a Ko. Invalid move")
					return False
			else:
				return False
		else:
			return False


	# keeps track of the SGF Tree for outputting
	def _update_sgf_tree(self, grid_pt, game_state):
	
		node = self.sgf_game.extend_main_sequence()
		
		if game_state.variation == False:
			node.set_move(grid_pt.color, (grid_pt.sgf_x, grid_pt.sgf_y))
		elif game_state.variation == True:
			var_str = str(game_state.variation_num)
			node.set('LB', [((grid_pt.sgf_x, grid_pt.sgf_y), var_str)])
		else:
			raise ValueError

	# the main entry point into board logic and board updating
	def update(self, grid_pt, game_state):
	
		#self.working_state = copy
		
		if game_state.variation == True:
			clicked_sq = self.board[grid_pt.np_x, grid_pt.np_y]
			if clicked_sq.is_blnk():
				# print("variation set Before")
				# print(self.board[grid_pt.np_x, grid_pt.np_y].variation_n
				clicked_sq.variation_num = game_state.variation_num
	
				self.board_hist.append(copy.deepcopy(self.board))
				self._update_sgf_tree(grid_pt, game_state) 
			return True
		
		# make sure move is valid before placing
		elif (grid_pt.color == 'w' or grid_pt.color == 'b'):
			if self._is_valid(grid_pt):
				print("The piece is valid, getting placed")
				self._place_piece(grid_pt)
				self._life_and_death(grid_pt)
				self.board_hist.append(copy.deepcopy(self.board))
				
				# update SGF tree
				self._update_sgf_tree(grid_pt, game_state) 
				return True
			else:
				return False
		else:
			raise ValueError


# why is this outside by itself? TODO
def in_board(elem, sz):
	if (elem[0] >= 0 and elem[0] < sz
		and elem[1] >= 0 and elem[1] < sz):
		return True
	else:
		return False
	
# function for opening an sgf from game_gui.py
def open_sgf(game):
  
	komi = game.get_komi()
	board_sz = game.get_size()
	
	
	moves = game.get_main_sequence() # ls of Tree_node
	##print(moves)
	for elem in moves:
		print("~~~")
		print("elem", elem)
		if elem.has_property("B") or elem.has_property("W"):
			print("its a move ", elem.get_move())
		elif elem.has_property("LB"):
			print("its a label ", elem.get('LB'))
	
	#my_array = np.ndarray(shape = (board_sz, board_sz), dtype=object)
	
	
	#new_board = bd.Game(komi, my_array)
