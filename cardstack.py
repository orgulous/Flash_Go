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
		
	def get_len(self):
		return len(self.hand_file_ls)
		
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
		 
	# removes the top card of testing, and returns a filename
	# if empty list, return None
	def draw_from_hand(self):
		if self.get_len() != 0:
			end_ind = len(self.hand_file_ls) - 1
			card_filename = self.hand_file_ls.pop(end_ind)
			return card_filename
		elif self.get_len() == 0:
			return None
		else:
			ValueError

		
	def _update_json(self, card):
		self.json_file = open(
			"./json/card_data.json", "r+")
			
		# list of all sgf filenames in deck
		self.json_values = self._load_json(self.json_file)
	
		card_f = card.filename
		card_val = self.json_values[card_f]
		
		card_val['date_due'] = card.date_due
		card_val['date_last_reviewed'] = card.date_last_reviewed
		card_val['space_level'] = card.space_level
		
		self.json_file.seek(0) # go to beginning
		json.dump(self.json_values, self.json_file)
		self.json_file.close()
		
	# when the card is answered correctly
	def reinsert_to_deck(self, card, familiarity):
		self.json_file = open(
			"./json/card_data.json", "r+")
			
		# update the familiarity & json
		card.incr_time(familiarity)
		self._update_json(card)
		
		# no need to reinsert into hand
		# deck already updated
	
	# when the card is answered incorrectly
	# adds the card to the bottom. Also resets time
	def reinsert_to_hand(self, card):
		card.reset_prog()
		self._update_json(card)
		self.hand_file_ls.insert(0, card.filename)
	
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
	
		
		
		