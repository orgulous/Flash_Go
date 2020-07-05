# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import tkinter as tk
import gameframe as gf
import cardframe as cf


LARGE_FONT= ("Verdana", 12)


class FlashGo(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self, bg = 'red')
		
		container.pack(side="top", fill="both", expand = False)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		
		self.frames = {}

		for F in (StartPage, gf.EditFrame, cf.CardFrame):
			page_name = F.__name__
			frame = F(container, self)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="n")
			#frame.grid_columnconfigure()

		self.show_frame("StartPage") #self.destroy()

	def show_frame(self, page_name):
		for fme in self.frames:     # Remove all frames
			self.frames[fme].grid_remove()
		frame = self.frames[page_name]
		#frame.tkraise()
		frame.grid() 

class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self,parent)
		
		label = tk.Label(self, text="Welcome to FlashGo", font=LARGE_FONT)
		label.pack(pady=10,padx=10, side = "top")

		button = tk.Button(self, text="Go Problem Flashcards", command=lambda: controller.show_frame("CardFrame"))
		button.pack()
		
		button2 = tk.Button(self, text="Edit Cards", command=lambda: controller.show_frame("EditFrame"))
		button2.pack()

app = FlashGo()
app.minsize(500, 100) #fix this somehow later 
app.mainloop()
