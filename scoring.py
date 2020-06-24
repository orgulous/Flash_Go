import numpy as np
import board as bd

# This class scores the board
class Scoring:

	def __init__(self, game):
		self.board = game.board
		self.komi = game.komi
		self.board_sz = len(game.board)
		self.prisoners = game.prisoners
		self.score = {'b': 0, 'w': 0}
		
		# sets for calculating score inside recursion 
		# global variables prevent storing sets recursively, much better 
		# performance for scoring
		self.blank_set = set([])
		self.stone_set = set([])

		# we do not want to go over blanks twice
		self.seen_board = np.zeros(shape = (self.board_sz, self.board_sz))

	# add up the score given list of blanks for a particular 'patch'
	def _add_score(self):
		potential_score = len(self.blank_set)
		# must decide if 'Dame' for scoring  
		has_white = False
		has_black = False

		# check for black and white in stone_ls
		for coord in self.stone_set:
			if self.board[coord[0], coord[1]] == -1:
				has_black = True
			elif self.board[coord[0], coord[1]] == 1:
				has_white = True
		
		# exclusive or to check for 'dame'
		if has_black ^ has_white:
			
			# second condition to prevent scoring 1st and second move of game
			if has_black and (potential_score < self.board_sz ** 2 - 2):
				self.score['b'] += potential_score
			elif has_white and (potential_score < self.board_sz ** 2 - 2): 
				self.score['w'] += potential_score
			else:
				pass

	# recursively counts for score 
	# main logic for counting score
	def _flood_fill_cnt(self, start):
		row, col  = start[0], start[1]

		up = (row - 1, col)
		down = (row + 1, col)
		left = (row, col - 1)
		right = (row, col + 1)
		directions = [up, down, left, right]

		# We need fast performance - need to check if valid BEFORE we recurse
		if self.board[row, col] == 0: # it's a blank. keep counting score.

			# track blanks for this particular area
			self.blank_set.add((row, col))
			# track overall grid seen
			self.seen_board[row, col] = 1 # set it equal to 1

			# go recurse in four directions
			for direction in directions:
				if (bd.in_board(direction, self.board_sz) 	
					and direction not in self.blank_set):
					self._flood_fill_cnt(direction)

		elif self.board[row, col] != 0: # It is a stone. Stop looking 
			self.stone_set.add((row, col))
			return
		else:
			raise ValueError

		return 

	# score each of the positions by counting territories surrounded by colors
	# returns a final score
	def score_it(self):

		# find all 'patches' of empty board spaces surrounded by a color
		for i in range(self.board_sz):
			for j in range(self.board_sz):
				
				# make sure you don't count the same patch twice
				if self.seen_board[i, j] == 0:
					self._flood_fill_cnt((i, j))

					# remove duplicates, then add the score up using 
					if len(self.blank_set) > 0:
						self._add_score()

					# reset after this scoring
					self.blank_set = set([])
					self.stone_set = set([])

		# count opposite color which is captured, and add to score
		black_score = self.score[-1] + self.prisoners[1]
		white_score = self.score[1] + self.prisoners[-1]

		final_score = {-1: black_score, 1: white_score + self.komi} 
		return final_score

