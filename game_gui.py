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
		self.right_frame = tk.Frame(self.root)

		# text variables for the labels
		self.brush_mode_txt = tk.StringVar()
		
		# actual labels for storing info
		self.brush_mode_lab = None

		# stores references to each label for new update
		self.label_grid = np.ndarray(shape=(size,size), dtype=object)

		self._set_gui_values()

	def _set_gui_values(self):

		# create root values
		self.root.title("Go Game")
		self.root.resizable(width = 0, height = 0)

		# tells how to pack the elements inside of the frame 
		self.top_frame.pack(side = tk.TOP, fill = tk.X, padx = 20, pady = 10)
		self.right_frame.pack(side = tk.RIGHT)
		self.game_frame.pack(fill = "none", expand = True, padx = 20)
		self.bottom_frame.pack(side = tk.BOTTOM, fill = tk.X)
		
		
		self.brush_mode_txt.set("")
		self.brush_mode_lab = tk.Label(self.bottom_frame, textvariable = self.brush_mode_txt, height = 3)
		self.brush_mode_lab.pack(side = tk.LEFT, padx = 20)
		

		###############
		
		# Add the new game button
		self.bt = tk.Button(self.top_frame, text = "New Game", command = self._new_game_on_click)
		self.bt.pack(side = tk.LEFT, fill = tk.X)
		
		# save SGF button
		self.bt = tk.Button(self.top_frame, text = "Save", command = self._save_on_click)
		self.bt.pack(side = tk.LEFT, fill = tk.X)

		# open SGF button
		self.bt = tk.Button(self.top_frame, text = "Open",  command = self._open_on_click)
		self.bt.pack(side = tk.LEFT, fill = tk.X)

		# Add the variations button
		self.bt_numbers = tk.Button(self.right_frame, text = "Numbers", command = self._variation_on_click)
		self.bt_numbers.pack(side = tk.TOP, fill = tk.X)

		# Problem button
		self.bt_answers = tk.Button(self.right_frame, text = "Answers",  command = self._answers_on_click)
		self.bt_answers.pack(side = tk.BOTTOM, fill = tk.X)
		
		# B/W button
		self.bt_turns = tk.Button(self.right_frame, text = "B/W",  command = self._turns_on_click)
		self.bt_turns.pack(side = tk.BOTTOM, fill = tk.X)
		self.bt_turns.config(relief = tk.SUNKEN)
			
	# second callback to change text of button while running for new game
	def _new_game_on_click(self):
		self.my_game = gm.Game(self.size)

		self.game_state = moves.GameState()

		#self.new_game_bt_txt.set("New Game")
		self.turn = 'w'
		
		# store the reference to label into here for future use
		for i in range(self.size):
			for j in range(self.size):
				label = self.label_grid[i,j]
				label.config(text=str(""), compound = 'center')
		
		self._gui_update()

	# stored action for moving to problems
	def _turns_on_click(self):
		self.game_state.make_turns()
		self.bt_turns.config(relief = tk.SUNKEN)
		self.bt_answers.config(relief = tk.RAISED)
		self.bt_numbers.config(relief = tk.RAISED)
		
	# stored action for moving to problems
	def _answers_on_click(self):
		self.game_state.make_answers()
		self.bt_numbers.config(relief = tk.RAISED)
		self.bt_answers.config(relief = tk.SUNKEN)
		self.bt_turns.config(relief = tk.RAISED)
		
	# stored action for moving to variations
	def _variation_on_click(self):
		self.game_state.make_numbers()
		self.game_state.variation_num = 0
		self.bt_numbers.config(relief = tk.SUNKEN)
		self.bt_turns.config(relief = tk.RAISED)
		self.bt_answers.config(relief = tk.RAISED)
		
	
	# Open an SGF file
	def _open_on_click(self):
		self._new_game_on_click()
		self.game_state = moves.GameState()
		
		filename = filedialog.askopenfilename()
		self.my_game = self.my_game._open_sgf(filename)
		self._gui_update()
		
	# stored action for new game on click
	def _save_on_click(self):
		self.my_game.save_game()
	
	# initially creates all the labels for the board
	def create_board(self):
		my_board = self.my_game.board
		im_blnk = tk.PhotoImage(file='./img/center.gif')
		
		for i in range(self.size):
			for j in range(self.size):
				# try only updating when board changes
				lab = tk.Label(self.game_frame, image = im_blnk, padx=0, pady=0, bd=0)
				lab.image = im_blnk

				# store the reference to label into here for future use
				self.label_grid[i,j] = lab
				lab.grid(row=i,column=j, padx = (0, 0), pady = (0,0))
				lab.bind('<Button-1>',lambda e,i=i,j=j: self._on_click(i,j,e))
			
	
	# All of these get new text values of the status bar
	def _update_status(self):
		new_text = self.game_state.brush.value
		'''
		self.brush_mode_txt.set(new_text)
		self.brush_mode_lab.config(textvariable = self.brush_mode_txt)
		'''

	def _is_int(self, s):
		try: 
			int(s)
			return True
		except ValueError:
			return False

	# updates the images in the cell
	def _alter_board_cell(self, my_board, i, j):
		
		im_blck = tk.PhotoImage(file='./img/black.gif')
		im_wht = tk.PhotoImage(file='./img/white.gif')
		im_blnk = tk.PhotoImage(file='./img/center.gif')

		label = self.label_grid[i,j]
		
		my_grid_sq = my_board[i,j]
		symbol = my_grid_sq.symbol
		
		if self._is_int(symbol):
			label.config(text=symbol, compound = 'center', font =('Helvetica', 18, 'bold'))
		#print("bd_var_num ", bd_var_num)
		elif symbol == 'answers':
			label.config(text="‎✔", fg = "green", 
				compound = 'center', font =('Helvetica', 20, 'bold'))	
		elif symbol == 'black':
			label.configure(im = im_blck)
			label.image = im_blck
		elif symbol == 'white':
			label.configure(im = im_wht)
			label.image = im_wht
		elif symbol == 'blank':
			label.configure(im = im_blnk)
			label.image = im_blnk
		else:
			print("no value for symbol in this grid square", symbol)
			raise ValueError

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

		for i in range(self.size):
			for j in range(self.size):
				# only updates cell if changed. Otherwise takes too long
				if self._board_changed(my_board, i, j) or len(self.my_game.board_hist) < 2:
				
					#print("Board changed at ", i , j)
					self._alter_board_cell(my_board,i, j)
	

	# turns the board game into the right one
	def _gui_update(self):
		self._update_board()
		self._update_status()

	# continue to wait for the event. This is the main updating loop
	def _on_click(self, i, j, event):
		print("~~~~~~~~~~~~~~~~~~~~~~")
		print("~~~~~~~~~~~~~~~~~~~~~~")
		
		my_brush = self.game_state.brush

		# calculated what symbol to used based on the state
		symbol = moves.calc_symbol(self.game_state)
		print("symbol just calculated:", symbol)
			
		grid_sq = moves.GridSquare(i, j, symbol, self.size)
		
		# all logic on board updating is contained here
		# takes the game board and then updates it.
		
		#print("grid_sq.my_state.problem", grid_sq.problem)
		successful_move = self.my_game.update(grid_sq, self.game_state) 
		
		if successful_move:
			print("successful move at, ", grid_sq.np_x, grid_sq.np_y)
			
			self._gui_update()
			
			# Flip if not a pass
			if (my_brush == moves.Brush('turns')):
				self.game_state.flip_turns()

my_game_gui = Game_Gui(9)
my_game_gui.create_board()
my_game_gui.root.mainloop()
