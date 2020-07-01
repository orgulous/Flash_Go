import numpy as np
import moves
import card
from sgfmill import sgf, sgf_moves, ascii_boards
from sgfmill import boards
import copy
import gamelogic as gl

class Game:
	def __init__(self, size):

		# numpy array of GridSquares
		self.board = self._init_board(size) 
		self.board_sz = size
		self.sgf_game = sgf.Sgf_game(size=size)

		# keeps track of board history for 'ko' rule
		self.board_hist = [copy.deepcopy(self.board)] 
		# self.liberties = 0
		# self.same_col_set = set([])
		
	def _init_board(self, size):
		my_array = np.ndarray(shape = (size, size), dtype=object)
		for x in range(size):
			for y in range(size):
				my_array[x,y] = moves.GridSquare(x, y, 'blank', size)

		return my_array
	
	
	# function for opening an sgf from game_gui.py
	def _open_sgf(self, filename):
	  
		f = open(filename, "rb")
		sgf_src = f.read()
		f.close()
		sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
		board, plays = sgf_moves.get_setup_and_moves(sgf_game)
		
		sz = sgf_game.get_size() 
		
		# makes new game
		new_game = Game(sz)
		my_array = new_game.board
		print(plays)
		for color, move in plays:
			if move is None:
				continue
			row, col = move
			row = (new_game.board_sz - 1) - row
			if color == 'b':
				color = 'black'
			if color == 'w':
				color = 'white'
			
			try:
				my_array[row,col] = moves.GridSquare(row, col, color, sz)
				#board.play(row, col, colour)
			except ValueError:
				raise Exception("illegal move in sgf file")
		
		game_nodes = sgf_game.get_main_sequence()
		
		for node in game_nodes:
			if node.has_property("LB"):
				node_vals = node.get("LB")[0]
				row = (new_game.board_sz - 1) - node_vals[0][0]
				col = node_vals[0][1]
				sym = node_vals[1]
				print(sym, row, col)
				
				my_array[row,col] = moves.GridSquare(row, col, sym, sz)
		
		return new_game
	
	
	# method to return game tree
	def save_game(self):
		card.add_card(self.sgf_game)

	# keeps track of the SGF Tree for outputting
	def _update_sgf_tree(self, grid_sq, game_state):
		my_brush = game_state.brush
	
		node = self.sgf_game.extend_main_sequence()
		if my_brush == moves.Brush('answers'):
			print("setting a problem node")
			node.set('LB', [((grid_sq.sgf_x, grid_sq.sgf_y), "answers" )])
		elif my_brush == moves.Brush('turns'):
			color = None
			if grid_sq.symbol == "black":
				color = 'b'
			else:
				color = 'w'
			
			node.set_move(color, (grid_sq.sgf_x, grid_sq.sgf_y))
		elif my_brush == moves.Brush('numbers'):
			print("In SGF Tree Setting to ", grid_sq.symbol)
			node.set('LB', [((grid_sq.sgf_x, grid_sq.sgf_y), grid_sq.symbol)]) # sets the numbers instring
		else:
			raise ValueError

	# the main entry point into board logic and board updating
	def update(self, grid_sq, game_state):
		if game_state.brush == moves.Brush('answers'):
			clicked_sq = self.board[grid_sq.np_x, grid_sq.np_y]
			if clicked_sq.is_blnk():
				clicked_sq.symbol = 'answers'
				self.board_hist.append(copy.deepcopy(self.board))
				self._update_sgf_tree(grid_sq, game_state) 
				return True	
			else:
				return False
		
		elif game_state.brush == moves.Brush('numbers'):
			clicked_sq = self.board[grid_sq.np_x, grid_sq.np_y]
			if clicked_sq.is_blnk():
				clicked_sq.symbol = grid_sq.symbol
				self.board_hist.append(copy.deepcopy(self.board))
				self._update_sgf_tree(grid_sq, game_state) 
				return True
			else:
				return False
		
		# make sure move is valid before placing
		elif game_state.brush == moves.Brush('turns'):
			my_logic = gl.GameLogic(self.board, self.board_hist,self.board_sz)
			
			if my_logic.is_valid(grid_sq, self.board):
				self.board = my_logic.run_move(grid_sq)
				self.board_hist.append(copy.deepcopy(self.board))
				self._update_sgf_tree(grid_sq, game_state) 
				return True
			else: 
				return False	
		else:
			raise ValueError


