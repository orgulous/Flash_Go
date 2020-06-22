import tkinter as tk
import numpy as np
import board as bd 
import scoring as sc
from sgfmill import sgf
from tkinter import messagebox, simpledialog

class Game_Gui:

	def __init__(self, size, komi):
		# game logic elements
		self.turn = -1		
		self.komi = komi
		self.size = size
		self.my_game = bd.Game(komi, (np.zeros(shape = (size, size))).astype('int'))
	
		# gui elements
		self.root = tk.Tk()
		# place these frames into the root
		self.top_frame = tk.Frame(self.root)
		self.game_frame = tk.Frame(self.root)
		self.bottom_frame = tk.Frame(self.root)

		# text variables for the labels
		self.prisoners = tk.StringVar()
		self.the_turn = tk.StringVar()
		self.my_score = tk.StringVar()
		self.new_game_bt_txt = tk.StringVar()
		self.save_bt_txt = tk.StringVar()
		
		# actual labels for storing info
		self.pris_lab = None
		self.turn_lab = None
		self.score_lab = None

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
		self.prisoners.set("Black's Prisoners: 0   White's Prisoners: 0")
		self.my_score.set("Black Score: 0   White Score: 5.5")
		self.new_game_bt_txt.set("New Game")
		self.save_bt_txt.set("Save")

		self.turn_lab = tk.Label(self.top_frame, textvariable = self.the_turn, height = 3)
		self.turn_lab.pack(side = tk.LEFT, padx = 20)
		self.pris_lab = tk.Label(self.bottom_frame, textvariable = self.prisoners, height = 3)
		self.pris_lab.pack(side = tk.LEFT, padx = 20)
		self.score_lab = tk.Label(self.bottom_frame, textvariable = self.my_score, height = 3)
		self.score_lab.pack(side = tk.RIGHT, padx = 20)

		# Add the passing button
		self.bt = tk.Button(self.top_frame, text = "Pass", command = self._pass_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)
		
		#TODO add a new button for "open SGF"
		#This will copy the SGF tree format into my format

		# Add the new game button
		self.bt = tk.Button(self.top_frame, textvariable = self.new_game_bt_txt, 
			command = self._new_game_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)

		#TODO add a new button for "save SGF"
		self.bt = tk.Button(self.top_frame, text = "Save", textvariable = self.save_bt_txt, command = self._save_on_click)
		self.bt.pack(side = tk.RIGHT, fill = tk.X)

	# second callback to change text of button while running for new game
	def _new_game_callback(self):
		self.my_game = bd.Game(self.komi, (np.zeros(shape = (self.size, self.size))).astype('int'))
		self.turn = 1
		self.the_turn.set("Turn: Black")
		self._gui_update()
		self.new_game_bt_txt.set("New Game")
		self.turn = -1

	# stored action for new game on click
	def _new_game_on_click(self):
		self.new_game_bt_txt.set("Clearing Board...")
		self.root.after(9, self._new_game_callback)
	
	# stored action for playing passing on click
	def _pass_on_click(self):
		move = (0, 0, 0) # final zero means pass
		successful_move = self.my_game.update(move) 

		if successful_move:
			self._gui_update()
			self.turn = bd.flip(self.turn) # after turn ends, you flip
			
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

	# updates the score every click
	def _update_score(self):
		score_obj = sc.Scoring(self.my_game)
		score_dict = score_obj.score_it()
		score_sts = "Black Score: " + str(score_dict[-1]) + "   " \
			+ "White Score: " + str(score_dict[1])
		self.my_score.set(score_sts)

	# All of these get new text values of the status bar
	def _update_status(self):

		# 1 - update prisoners
		prsn = self.my_game.prisoners
		# captured prisoners are opposite color
		prsn_sts = "Black's Prisoners: " + str(prsn[1]) + "   " \
			+ "White's Prisoners: " + str(prsn[-1])
		self.prisoners.set(prsn_sts)
		
		# 2 - update turn (oppsite turn now)
		flip_turn = bd.flip(self.turn) 
		turn_txt = "Black" if flip_turn == -1 else "White"
		turn_sts = "Turn: " + turn_txt 
		self.the_turn.set(turn_sts)
		
		# 3 - update score
		self._update_score()

	# initially creates all the labels for the board
	def create_board(self):
		my_board = self.my_game.board
		im_blck = tk.PhotoImage(file='./img/black.gif')
		im_wht = tk.PhotoImage(file='./img/white.gif')
		im_blnk = tk.PhotoImage(file='./img/blank.gif')
		for i in range(self.size):
			for j in range(self.size):
				# try only updating when board changes
				if my_board[i,j] == 0:
					lab = tk.Label(self.game_frame, image = im_blnk, bd=0)
					lab.image = im_blnk
				elif my_board[i,j] == 1:
					lab = tk.Label(self.game_frame, image = im_wht, bd=0)
					lab.image = im_wht
				elif my_board[i,j] == -1:
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
		im_blnk = tk.PhotoImage(file='./img/blank.gif')

		label = self.label_grid[i,j]
		if my_board[i,j] == 1:
			label.configure(im = im_wht)
			label.image = im_wht
		elif my_board[i,j] == 0:
			label.configure(im = im_blnk)
			label.image = im_blnk
		elif my_board[i,j] == -1:
			label.configure(im = im_blck)
			label.image = im_blck
		else:
			raise ValueError

	# test to see if board changed in a spot, to see if you need new label
	def _board_changed(self, my_board, i, j):
		try:
			old_state = self.my_game.board_hist[-2][i, j]
			new_state = my_board[i,j]
			if old_state == new_state:
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
		move = i, j, self.turn

		# all logic on board updating is contained here
		successful_move = self.my_game.update(move) 

		# takes the game board and then updates it.
		if successful_move:
			self._gui_update()
			self.turn = bd.flip(self.turn) # after turn ends, you flip

my_game_gui = Game_Gui(9, 5.5)
my_game_gui.create_board()
my_game_gui.root.mainloop()

