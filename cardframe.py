import tkinter as tk
from tkinter import ttk

import game as gm
import moves 
import numpy as np
import cardstack as cs
import card as cd

class CardFrame(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.config(bg='white')
		
		# game logic elements	
		size = 9
		self.size = size
		self.my_game = None # Game type
		self.card_stack = cs.CardStack()
		self.my_card_f = None # A string
		self.fam = None
		
		self.label_grid = np.ndarray(shape=(size,size), dtype=object)
		
		self._init_frames()
		self._add_nav_buttons(controller)
		self.create_board()
		self._pack_frames()
		self._add_time_buttons()
		
		# this should up set up the card state
		self._swap_board()
		self._update_board()
		
		
	def _init_frames(self):
		# place these frames into the root
		self.menu_frame = tk.Frame(self, bg = 'green')
		self.top_frame = tk.Frame(self)
		self.game_frame = tk.Frame(self, width = 200, bg = 'blue')
		self.bottom_frame = tk.Frame(self)

		self.separator = ttk.Separator(self, orient='horizontal')

	# does the 1st top part 
	def _add_nav_buttons(self, controller):
		self.menu_frame.pack(expand = True, fill = tk.X, padx = 20)
		label = tk.Label(self.menu_frame, text="Mode: Learning Cards")
		label.pack(pady=10, side = tk.TOP, expand = True, fill = 'both')
		label.config(font=("Calibri", 30))

		button1 = tk.Button(self.menu_frame, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
		button1.pack(fill = tk.X, side = tk.LEFT)

		button2 = tk.Button(self.menu_frame, text="Edit Cards", command=lambda: controller.show_frame("EditFrame"))
		button2.pack(side = tk.LEFT, fill = tk.X)
		
		self.separator.pack(side='top', fill='x', pady=5)
		
	# PACKS and sets values
	def _pack_frames(self):

		# tells how to pack the elements inside of the frame 
		self.top_frame.pack(side = tk.TOP, fill = tk.X, padx = 20, pady = 10)
		#self.right_frame.pack(side = tk.RIGHT, padx = 8)
		self.game_frame.pack(padx = 20)
		self.bottom_frame.pack(side = tk.BOTTOM, fill = tk.X)

	def _add_time_buttons(self):
		self.button1 = tk.Button(
			self.bottom_frame, text="wrong",
			state = "disabled",
			command = lambda: self._wrong_ans_act())
		self.button1.pack(fill = tk.X, side = tk.LEFT)
	
		self.button2 = tk.Button(
			self.bottom_frame, text="ok",
			state = "disabled",
			command = lambda: self._right_ans_act("ok"))
		self.button2.pack(fill = tk.X, side = tk.LEFT)
		
		self.button3 = tk.Button(
			self.bottom_frame, text="good",
			state = "disabled",
			command = lambda: self._right_ans_act("good"))
		self.button3.pack(fill = tk.X, side = tk.LEFT)
		
		self.button4 = tk.Button(
			self.bottom_frame, text="great",
			state = "disabled",
			command = lambda: self._right_ans_act("great"))
		self.button4.pack(fill = tk.X, side = tk.LEFT)
		
	def _disable_buttons(self):
		self.button1.configure(state='disabled')
		self.button2.configure(state='disabled')
		self.button3.configure(state='disabled')
		self.button4.configure(state='disabled')
		
	def _change_buttons(self, correct):
		if correct == "right":
			self.button2.configure(state='normal')
			self.button3.configure(state='normal')
			self.button4.configure(state='normal')
		elif correct == "wrong":
			self.button1.configure(state='normal')
		

	def create_board(self):
		im_blnk = tk.PhotoImage(file='../Flash_Go/img/center.gif')
		
		for i in range(self.size):
			for j in range(self.size):
				lab = tk.Label(self.game_frame, image = im_blnk,  padx=0, pady=0, bd=0)
				lab.image = im_blnk

				# store the reference to label into here for future use
				self.label_grid[i,j] = lab
				lab.grid(row=i,column=j, padx = (0, 0), pady = (0,0))
				lab.bind('<Button-1>',lambda e,i=i,j=j: self._on_click(i,j,e))
	
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
			
	def _clear_labels(self):
		for i in range(self.size):
			for j in range(self.size):
				label = self.label_grid[i,j]
				label.config(text=str(""), compound = 'center')

	# updates board. called when something happens to board
	def _update_board(self):
		my_board = self.my_game.board

		for i in range(self.size):
			for j in range(self.size):
				self._alter_board_cell(my_board,i, j)
	
	def _swap_board(self):
		self.my_game = gm.Game(self.size)
	
		self.my_card_f = self.card_stack.draw_from_hand()
		if self.my_card_f != None:
			self.top_card = cd.Card(self.my_card_f)
			filepath = "./sgf_files/" + self.my_card_f
			self.my_game = gm.open_sgf(filepath)
		else:
			print("no more cards in hand")
		
	# turns the board game into the right one
	def _gui_update(self):
		self._clear_labels()
		self.my_game = gm.Game(self.size)
		self._swap_board()
		self._update_board()
			
	def _wrong_ans_act(self):	
		# reset the card values
		# reinsert the card to hand
		
		cs = self.card_stack
		cs.reinsert_to_hand(self.top_card)
		
		self._disable_buttons()
		self._gui_update()

	# need to wait for a button to fire to reinsert
	def _right_ans_act(self, fam):
		cs = self.card_stack
		cs.reinsert_to_deck(self.top_card, fam)

		self._disable_buttons()
		self._gui_update()
	
	# continue to wait for the event. This is the main updating loop
	def _on_click(self, i, j, event):
		print("~~~~~~~~~~~~~~~~~~~~~~")
		
		game_sym = self.my_game.get_symbol(i, j)
		print("This is the symbol on the grid you clicked: ",
			game_sym)
		
		if game_sym == "answers":
			print("the correct thing was pressed")
			self._change_buttons("right")
			
		else:
			print("you clicked the wrong place")
			# update the buttons
			self._change_buttons("wrong")


