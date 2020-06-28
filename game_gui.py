import tkinter as tk
import numpy as np
import game as gm 
import moves
from sgfmill import sgf, sgf_moves, ascii_boards
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk

class Game_Gui:

	def __init__(self, size):
		# game logic elements	
		self.size = size
		self.my_game = gm.Game(size) # Game type
		self.game_state = moves.GameState()
	
		# gui elements
		self.root = tk.Tk()
		# place these frames into the root
		self.top_frame = tk.Frame(self.root)
		self.game_frame = tk.Frame(self.root)
		self.bottom_frame = tk.Frame(self.root)

		# text variables for the labels
		self.the_turn = tk.StringVar(value="Turn: Black")

		self.new_game_bt_txt = tk.StringVar()
		self.save_bt_txt = tk.StringVar()
		
		# actual labels for storing info
		self.turn_lab = None

		# stores references to each label for new update
		self.label_grid = np.ndarray(shape=(size,size), dtype=object)

		self._set_gui_values()

	def _set_gui_values(self):

		# create root values
		self.root.title("Go Game")
		self.root.resizable(width = 0, height = 0)

		# tells how to pack the elements inside of the frame 
		self.top_frame.pack(side = tk.TOP, fill = tk.X)
		self.game_frame.pack(fill = "none", expand = True)
		self.bottom_frame.pack(side = tk.TOP, fill = tk.X)

		# set default text values for status var
		self.new_game_bt_txt.set("New Game")
		self.save_bt_txt.set("Save")

		self.turn_lab = tk.Label(self.top_frame, textvariable = self.the_turn, height = 3)
		self.turn_lab.pack(side = tk.LEFT, padx = 30)
		self.pris_lab = tk.Label(self.bottom_frame, textvariable = " ", height = 3)
		self.pris_lab.pack(side = tk.LEFT, padx = 20)

		# Add the new game button
		self.bt = tk.Button(self.top_frame, textvariable = self.new_game_bt_txt, 
			command = self._new_game_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)

		# Add the variations button
		self.bt = tk.Button(self.top_frame, text = "Variation", command = self._variation_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)
		
		# save SGF button
		self.bt = tk.Button(self.top_frame, text = "Save", textvariable = self.save_bt_txt, command = self._save_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)
	
		# open SGF button
		self.bt = tk.Button(self.top_frame, text = "Open",  command = self._open_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)

		# open SGF button
		self.bt = tk.Button(self.top_frame, text = "Problem",  command = self._problem_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)
			
	# second callback to change text of button while running for new game
	def _new_game_on_click(self):
		self.my_game = gm.Game(self.size)

		self.game_state = moves.GameState()
		#self.game_state.turn = 'b'
		#self.game_state.variation_num = 0
		#self.game_state.variation = False
		#self.game_state
		self.the_turn.set("Turn: Black")
		self.new_game_bt_txt.set("New Game")
		self.turn = 'w'
		
		# store the reference to label into here for future use
		for i in range(self.size):
			for j in range(self.size):
				label = self.label_grid[i,j]
				label.config(text=str(""), compound = 'center')
		
		self._gui_update()
		
		# stored action for moving to variations
	def _problem_on_click(self):
		self.game_state.variation = False
		
		self.game_state.make_problem()
		
		print("variation", self.game_state.variation)
		print("problem", self.game_state.problem)
	
	# stored action for moving to variations
	def _variation_on_click(self):
	
		self.game_state.problem = False
		self.game_state.make_variation()
		self.game_state.variation_num = 0
		
		print("variation", self.game_state.variation)
		print("problem", self.game_state.problem)
		
	
	# Open an SGF file
	def _open_on_click(self):
		self._new_game_on_click()
		filename = filedialog.askopenfilename()
		self.my_game = gm.open_sgf(filename)
		
		
		# TODO needs to reflect actual new game state?
		self.game_state = moves.GameState()
		self._gui_update()
		
	# stored action for new game on click
	def _save_on_click(self):
		#game_name = simpledialog.askstring("Save as", "What do you want to name your sgf?", parent=self.root)
		self.my_game.save_game()
		
	# All of these get new text values of the status bar
	def _update_status(self):

		# 1 - update turn (oppsite turn now). Or update to variations
		
		if not self.game_state.is_variation():	
			turn_txt = "White" if self.game_state.turn == 'b' else "Black"
			turn_sts = "Turn: " + turn_txt 
		else:
			turn_sts = "Variations"
		self.the_turn.set(turn_sts)
		
	# initially creates all the labels for the board
	def create_board(self):
		my_board = self.my_game.board
		im_blck = tk.PhotoImage(file='./img/black.gif')
		im_wht = tk.PhotoImage(file='./img/white.gif')
		im_blnk = tk.PhotoImage(file='./img/center.gif')
		for i in range(self.size):
			for j in range(self.size):
				# try only updating when board changes
				bd_pt = my_board[i,j].color
				
				if bd_pt == 'blnk':
					lab = tk.Label(self.game_frame, image = im_blnk, padx=0, pady=0, bd=0)
					lab.image = im_blnk
				elif bd_pt == 'w':
					lab = tk.Label(self.game_frame, image = im_wht, bd=0)
					lab.image = im_wht
				elif bd_pt == 'b':
					lab = tk.Label(self.game_frame, image = im_blck, bd=0) 
					lab.image = im_blck
				else:
					raise ValueError

				# store the reference to label into here for future use
				self.label_grid[i,j] = lab
				lab.grid(row=i,column=j, padx = (0, 0), pady = (0,0))
				lab.bind('<Button-1>',lambda e,i=i,j=j: self._on_click(i,j,e))
			
	# updates the images in the cell
	def _alter_board_cell(self, my_board, i, j):
		
		im_blck = tk.PhotoImage(file='./img/black.gif')
		im_wht = tk.PhotoImage(file='./img/white.gif')
		im_blnk = tk.PhotoImage(file='./img/center.gif')

		label = self.label_grid[i,j]
		bd_pt = my_board[i,j].color
		

		bd_var_num = my_board[i,j].variation_num	
		bd_pt_prob = my_board[i,j].problem
		#print("bd_var_num", bd_var_num)
		#print("bd_pt_prob", bd_pt_prob)

		if bd_var_num != 0:
			label.config(text=str(bd_var_num), compound = 'center', font =('Helvetica', 18, 'bold'))
		#print("bd_var_num ", bd_var_num)
		elif bd_pt_prob:
			label.config(text="‎✔", fg = "green", 
				compound = 'center', font =('Helvetica', 20, 'bold'))	
		elif bd_pt == 'w':
			label.configure(im = im_wht)
			label.image = im_wht
		elif bd_pt == 'blnk':
			label.configure(im = im_blnk)
			label.image = im_blnk
		elif bd_pt == 'b':
			label.configure(im = im_blck)
			label.image = im_blck
		else:
			print("haven't gotten to more vairations")
			# raise ValueError

	# test to see if board changed in a spot, to see if you need new label
	def _board_changed(self, my_board, i, j):
		try:
			old_state_pt = self.my_game.board_hist[-2][i, j]
			new_state_pt = my_board[i,j]
			
			if old_state_pt.pt_is_equal(new_state_pt):
				return False
			else:
				return True
		except:
			return False

	# updates board. called when something happens to board
	def _update_board(self):
		# get current status of board from my_game instance
		my_board = self.my_game.board
		print("_update_board called")

		for i in range(self.size):
			for j in range(self.size):
				# only updates cell if changed. Otherwise takes too long
				if self._board_changed(my_board, i, j) or len(self.my_game.board_hist) < 2:
				
					self._alter_board_cell(my_board,i, j)
	

	# turns the board game into the right one
	def _gui_update(self):
		self._update_board()
		self._update_status()

	# continue to wait for the event. This is the main updating loop
	def _on_click(self, i, j, event):
		print("~~~~~~~~~~~~~~~~~~~~~~")
		print("~~~~~~~~~~~~~~~~~~~~~~")
		my_state = self.game_state
	
		if my_state.variation == True:
			my_state.variation_num = my_state.variation_num + 1
	
		grid_pt = moves.GridPoint(my_state.turn, i, j, my_state.variation_num, self.size, my_state.problem)
		
		# all logic on board updating is contained here
		# takes the game board and then updates it.
		print("grid_pt.my_state.problem", grid_pt.problem)
		successful_move = self.my_game.update(grid_pt, my_state) 
		
		
		if successful_move:
			print("successful move at, ", grid_pt.np_x, grid_pt.np_y)
			
			self._gui_update()
			
			# Flip if not a pass
			if (my_state.is_variation() == False):
				my_state.flip()

my_game_gui = Game_Gui(9)
my_game_gui.create_board()
my_game_gui.root.mainloop()
