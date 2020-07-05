# communicates between cards and JSON
import json
import datetime
import card as cd

class CardStack:

	def __init__(self):
		
		self.json_file = open(
			"./json/card_data.json", "r+")
			
		# list of all sgf filenames in deck
		self.json_values = self._load_json(self.json_file)
		
		# list of games to test still
		self.hand_file_ls = []
		
		self._draw_files_hand()
		
	# this should return the filenames of all the cards
	def _load_json(self, json_f):
		json_file = open("./json/card_data.json", "r+")
		json_values = json.load(json_file)
		json_file.close()
		return json_values
	
	# draws the files to be tested to the hand:
	def _draw_files_hand(self):
	
		# look through all keys for due cards
		for k in self.json_values:
			v = self.json_values[k]
			
			date_due_str = v["date_due"]
			date_last_reviewed_str = v["date_last_reviewed"]
			
			date_due_dt = datetime.datetime.strptime(
				date_due_str, "%S-%M-%H_%d-%m-%Y")
			
			
			if date_due_dt < datetime.datetime.now():
				self.hand_file_ls.append(k)
		 
	# removes the top card of testing, and returns it
	def draw_from_hand(self):
		end_ind = len(self.hand_file_ls) - 1
		card_filename = self.hand_file_ls.pop(end_ind)
		return card_filename
		
	# when the card is answered correctly
	# update the time of it. Update the Json entry
	def reinsert_to_deck(self, card, familiarity):
		card.incr_time(familiarity)
		
		card_f = card.filename
		card_to_insert = self.json_values[card_f]
		
		card_to_insert['date_due'] = card.date_due
		card_to_insert['date_last_reviewed'] = card.date_last_reviewed
		card_to_insert['space_level'] = card.space_level
		
		# self.hand_file_ls.remove(card_f)
	
	# when the card is answered incorrectly
	# adds the card to the bottom. Also resets time
	def reinsert_to_hand(self, card):
		self.hand_file_ls.insert(0, card.filename)
		pass
	
import unittest
class TestStringMethods(unittest.TestCase):
	
	def test_stack(self):
		print("test 1")
		my_stack = CardStack()
		
		orig_len = len(my_stack.hand_file_ls)
		
		print("Drawing a card from my hand")
		top_card_filename = my_stack.draw_from_hand()
		top_card = cd.Card(top_card_filename)
		
		inter_len = len(my_stack.hand_file_ls)
			
		print("This is my card on the board")
		print(top_card.space_level)
		print(top_card.date_created)
		print(top_card.date_last_reviewed)
		
		my_stack.reinsert_to_hand(top_card)
		
		new_len = len(my_stack.hand_file_ls)
		
		self.assertTrue(orig_len == new_len)
		self.assertTrue(orig_len - 1 == inter_len)

			
	def test_reinsertion(self):
		print("test 2")
		my_stack = CardStack()
		print("I have this many cards in my hand", 
			len(my_stack.hand_file_ls))
		
		print("Drawing a card from my hand")
		top_card_filename = my_stack.draw_from_hand()
		top_card = cd.Card(top_card_filename)
		
		top_card_name = top_card.filename
		level_pre = top_card.space_level
		create_pre = top_card.date_created
		reviewed_pre = top_card.date_last_reviewed
		
		print(level_pre, create_pre, reviewed_pre)
		
		my_stack.reinsert_to_deck(top_card, "ok")
		
		json_card = my_stack.json_values[top_card_name]
		level_post = json_card["space_level"]
		create_post = json_card["date_created"]
		reviewed_post = json_card["date_last_reviewed"]
		
		print(level_post, create_post, reviewed_post)
		
		self.assertFalse(
			(level_pre == level_post) &
			(create_pre == create_post) &
			(reviewed_pre == reviewed_post))
		
if __name__ == '__main__':
	unittest.main()
	
		
		
		