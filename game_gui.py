import tkinter as tk
import numpy as np
import board as bd 
import moves
from sgfmill import sgf, sgf_moves, ascii_boards
from tkinter import messagebox, simpledialog, filedialog

class Game_Gui:

	def __init__(self, size, komi):
		# game logic elements	
		self.komi = komi
		self.size = size
		self.my_game = self._make_game(size, komi)
		self.game_state = moves.GameState()
		# wrong self.my_game = bd.Game(komi, (np.array(shape = (size, size)), dtype=object))
	
		# gui elements
		self.root = tk.Tk()
		# place these frames into the root
		self.top_frame = tk.Frame(self.root)
		self.game_frame = tk.Frame(self.root)
		self.bottom_frame = tk.Frame(self.root)

		# text variables for the labels
		self.the_turn = tk.StringVar()

		self.new_game_bt_txt = tk.StringVar()
		self.save_bt_txt = tk.StringVar()
		
		# actual labels for storing info
		self.turn_lab = None

		# stores references to each label for new update
		self.label_grid = np.ndarray(shape=(size,size), dtype=object)

		self._set_gui_values()
		
	def _make_game(self, size, komi):
		my_array = np.ndarray(shape = (size, size), dtype=object)
		
		for x in range(size):
			for y in range(size):
				my_array[x,y] = moves.GridPoint('blnk', x, y, 0, size)
		
		new_board = bd.Game(komi, my_array)
		return new_board

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
		self.turn_lab.pack(side = tk.LEFT, padx = 20)
		self.pris_lab = tk.Label(self.bottom_frame, textvariable = "Whatever", height = 3)
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
			
	# second callback to change text of button while running for new game
	def _new_game_callback(self):
		self.my_game = self._make_game(self.size, self.komi)

		self.game_state.turn = 'b'
		self.game_state.variation_num = 0
		self.game_state.variation = False
		self.the_turn.set("Turn: Black")
		self._gui_update()
		self.new_game_bt_txt.set("New Game")
		self.turn = 'w'

	# stored action for new game on click
	def _new_game_on_click(self):
		self.new_game_bt_txt.set("Clearing Board...")
		self.root.after(9, self._new_game_callback)
		
	# stored action for moving to variations
	def _variation_on_click(self):
		self.game_state.make_variation()
	
	# Open an SGF file
	def _open_on_click(self):
		filename = filedialog.askopenfilename()
		f = open(filename, "rb")
		sgf_src = f.read()
		f.close()
		sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
		board, plays = sgf_moves.get_setup_and_moves(sgf_game)

		for colour, move in plays:
			if move is None:
				continue
			row, col = move
			try:
				board.play(row, col, colour)
			except ValueError:
				raise Exception("illegal move in sgf file")

		print(ascii_boards.render_board(board))
		#translate the board into my own board...
		self.game_state = moves.GameState()
		
	# Save the game into an sgf on clicking.
	def _save_callback(self, game_name):
		self.my_game.save_game(game_name)
		self.save_bt_txt.set("Save")

	# stored action for new game on click
	def _save_on_click(self):
		self.save_bt_txt.set("Saving...")
		game_name = simpledialog.askstring("Save as", "What do you want to name your sgf?",
                                parent=self.root)
		self.root.after(9, self._save_callback(game_name))
		
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
		im_blnk = tk.PhotoImage(file='./img/blank.gif')
		for i in range(self.size):
			for j in range(self.size):
				# try only updating when board changes
				bd_pt = my_board[i,j].color
				
				if bd_pt == 'blnk':
					lab = tk.Label(self.game_frame, image = im_blnk, bd=0)
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
		#print("Now altering, ", i, j)
		
		im_blck = tk.PhotoImage(file='./img/black.gif')
		im_wht = tk.PhotoImage(file='./img/white.gif')
		im_blnk = tk.PhotoImage(file='./img/blank.gif')
		im_1 = tk.PhotoImage(file='./img/v1.gif')
		im_2 = tk.PhotoImage(file='./img/v2.gif')

		label = self.label_grid[i,j]
		bd_pt = my_board[i,j].color
		

		bd_var_num = my_board[i,j].variation_num		
		#print("bd_var_num ", bd_var_num)
		
		# Need to do the variations 1st because they override
		if bd_var_num == 1:
			label.configure(im = im_1)
			label.image = im_1
		elif bd_var_num == 2:
			label.configure(im = im_2)
			label.image = im_2
					
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
		
		# various print statement diagnoses
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
	
		# TODO variation number
		grid_pt = moves.GridPoint(my_state.turn, i, j, my_state.variation_num, self.size)
		

		
		# all logic on board updating is contained here
		# takes the game board and then updates it.
		successful_move = self.my_game.update(grid_pt, my_state) 
		
		if successful_move:

			print("successful move at, ", grid_pt.np_x, grid_pt.np_y)
			
			self._gui_update()
			
			# Flip if not a pass
			if (my_state.is_variation() == False):
				my_state.flip()


my_game_gui = Game_Gui(9, 5.5)
my_game_gui.create_board()
my_game_gui.root.mainloop()

