import json
import datetime
import game as gm

class Card:
	def __init__(self, filename):
		
		# initialize 
		self.filename = filename
		self.filepath = "./sgf_files/" + filename
			
		self.game = gm.open_sgf(self.filepath)
		
		self.date_created = None
		self.space_level = None
		self.date_due = None
		self.date_last_reviewed = None
		
		self._set_card_from_json(filename)
		
	# get all the values from json and put into card
	def _set_card_from_json(self, filename):
		json_file = open("./json/card_data.json", "r+")
		json_values = json.load(json_file)
		card_content = json_values[filename]
		
		self.date_created = card_content[
			"date_created"]
		self.space_level = card_content[
			"space_level"]
		self.date_due = card_content["date_due"]
		self.date_last_reviewed = card_content[
			"date_last_reviewed"]
			
		json_file.close()

	def _level_to_time(self, familiarity):
		# ex, if spacelevel = 0, & ok,
		# then 1*(0+1) = 1
		# if spacelevel = 2, & good
		# then 2*(2+1) = 6
		mins_add = 0
		
		if familiarity == 'ok':
			mins_add = 1 * (self.space_level + 1)
		elif familiarity == 'good':
			mins_add = 2 * (self.space_level + 1)
		elif familiarity == 'great':
			mins_add = 3 * (self.space_level + 1)
		else: 
			raise ValueError
			
		return mins_add

	# takes in a time, and increments the 
	# date due field of Card object, and the Level
	def incr_time(self, familiarity):
	
		dt_now = datetime.datetime.now()
		dt_now_str = dt_now.strftime(
			"%S-%M-%H_%d-%m-%Y")
		
		mins_add = self._level_to_time(familiarity)
		
		new_dt = dt_now + datetime.timedelta(
			minutes = mins_add)
		new_dt_str = new_dt.strftime(
			"%S-%M-%H_%d-%m-%Y")
			
		self.date_due = new_dt_str
		self.space_level += 1
		self.date_last_reviewed = dt_now_str
		
		
import unittest
class TestStringMethods(unittest.TestCase):
	
	def test_read(self):
		my_card = Card("card_32-36-14_05-07-2020.sgf")
		
		print(my_card.date_last_reviewed)
		print(my_card.date_created)
		print(my_card.space_level)
		print(my_card.date_due)
		
		my_card.incr_time('ok')
	
		print("last reviewed", my_card.date_last_reviewed)
		print("created", my_card.date_created)
		print("level", my_card.space_level)
		print("due", my_card.date_due)
		

if __name__ == '__main__':
	unittest.main()
	
