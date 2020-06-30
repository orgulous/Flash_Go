import numpy as np
from sgfmill import sgf
from enum import Enum

def calc_symbol(game_state):
	# String Type
	symbol = None
	
	turn = game_state.turn
	brush = game_state.brush
	var_num = game_state.variation_num
	
	if brush == Brush('numbers'):
		game_state.variation_num += 1
		symbol = str(var_num)
	elif brush == Brush('answers'):
		symbol = 'check'
	elif brush == Brush('turns'):
		if turn == Turn('black'):
			symbol = 'black'
		elif turn == Turn('white'):
			symbol = 'white'
		else:
			print("symbol not found")
			raise ValueError
	else:
		print("symbol not found")
		raise ValueError

	return symbol
		
# This type goes into the numpy grid and tracks
# what is actually put in. It's a STONE but also a blank
class GridSquare:
	def __init__(self, np_x, np_y, symbol, size):
		self.symbol = symbol
			
		self.np_x = np_x
		self.np_y = np_y
		
		self.sgf_x = (size - 1) - self.np_x 
		self.sgf_y = self.np_y
	
	def get_sq_value(self):
		return self.symbol
		
	def is_blnk(self):
		if self.symbol == 'blank':
			return True
		else:
			return False
			
	def remove_stone(self):
		self.symbol = 'blank'
		
	def pt_is_equal(self, new_grid_sq):
		return self.symbol == new_grid_sq.symbol
		
# This type tracks the state of the game.
# It controls what kinds of pieces get placed on a click

class Turn(Enum):
	black = 'black'
	white = 'white'

class Brush(Enum):
	black = 'black'
	white = 'white'
	numbers = 'numbers'
	turns = 'turns'
	answers = 'answers'
			
class GameState:
	def __init__(self):
		self.brush = Brush('turns')
		self.turn = Turn('black')
		self.variation_num = 0
	
	# Turns on variation mode
	def make_white(self):
		self.brush = Brush('white')
		
	# Turns on variation mode
	def make_black(self):
		self.brush = Brush('black')
		
	# Turns on variation mode
	def make_numbers(self):
		self.brush = Brush('numbers')
		
	def make_turns(self):
		self.brush = Brush('turns')
		
	def make_answers(self):
		self.brush = Brush('answers')
	
	# function used to flip actual game state turn
	def flip_turns(self):
		if self.turn == Turn('black'): 
			self.turn = Turn('white')
		elif self.turn == Turn('white'): 
			self.turn = Turn('black')
		
# utility function used to flip turns in calculations, but not to change the game state
def flip(turn):
	if turn == 'black': 
		return 'white'
	elif turn == 'white': 
		return 'black'

