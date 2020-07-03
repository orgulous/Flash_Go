# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import tkinter as tk
import gameframe as gf


LARGE_FONT= ("Verdana", 12)


class FlashGo(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self)
		
		container.pack(side="top", fill="both", expand = False)

		self.frames = {}

		for F in (StartPage, gf.EditFrame, FlashCards):
			page_name = F.__name__
			print(page_name)
			frame = F(container, self)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="nsew")
			#frame.grid()

		self.show_frame("StartPage") #self.destroy()

	def show_frame(self, page_name):
		for fme in self.frames:     # Remove all frames
			self.frames[fme].grid_remove()
		frame = self.frames[page_name]
		frame.grid() 

class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self,parent)
		
		label = tk.Label(self, text="Start Page", font=LARGE_FONT)
		label.pack(pady=10,padx=10)

		button = tk.Button(self, text="Test Flashcards", command=lambda: controller.show_frame("FlashCards"))
		button.pack()
		
		button2 = tk.Button(self, text="Edit Cards", command=lambda: controller.show_frame("EditFrame"))
		button2.pack()


class FlashCards(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="FlashCards", font=LARGE_FONT)

		label.pack(pady=10,padx=10)

		button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
		button1.pack()

		button2 = tk.Button(self, text="Edit Cards", command=lambda: controller.show_frame("EditFrame"))
		button2.pack()


app = FlashGo()
app.minsize(500, 100) 
app.mainloop()
