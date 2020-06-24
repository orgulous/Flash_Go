import numpy as np
import board as bd
from sgfmill import sgf

# This type goes into the numpy grid and tracks
# what is actually put in. It's a STONE but also a blank
class GridPoint:
	def __init__(self, color, np_x, np_y, var_num, size):
		self.color = color # 'blnk', 'b', 'w'
		self.variation_num = var_num
		self.np_x = np_x
		self.np_y = np_y
		
		self.sgf_x = (size - 1) - self.np_x 
		self.sgf_y = self.np_y
		
	def is_blnk(self):
		if self.color == 'blnk':
			return True
		else:
			return False
			
	def remove_stone(self):
		self.color = 'blnk'
		
	def pt_is_equal(self, new_grid_pt):
		bool_col = self.color == new_grid_pt.color
		bool_var = self.variation_num == new_grid_pt.variation_num
		
		return bool_col and bool_var
		
# This type tracks the state of the game.
# It controls what kinds of pieces get placed on a click
class GameState:
	def __init__(self):
		self.turn = 'b' # 'blnk', 'b', 'w'
		self.mode = 0
		self.variation = False
		self.variation_num = 0
		
	# Turns on variation mode
	def make_variation(self):
		self.variation = not self.variation
	
	# function used to flip actual game state turn
	def flip(self):
		if self.turn == 'b': 
			self.turn = 'w'
		elif self.turn == 'w': 
			self.turn = 'b'

	def is_variation(self):
		return self.variation
	
		
# utility function used to flip turns in calculations, but not to change the game state
def flip(turn):
	if turn == 'b': 
		return 'w'
	elif turn == 'w': 
		return 'b'

