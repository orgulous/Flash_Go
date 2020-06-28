import json
import datetime

def get_card():
	return

def edit_card():
	return

def add_card(sgf_game):

	json_file = open("./json/card_data.json", "r+")
	cards = json.load(json_file)
	
	time = datetime.datetime.now()
	time_str = time.strftime("%S-%M-%H_%d-%m-%Y")	
	
	new_card = {
		"filename": "card_" + time_str + ".sgf",
		"date_created": time_str,
		"space_level" : 0,
		"date_last_reviewed": time_str,
		"date_due": time_str
	}
	
	card_ls = cards["cards"]
	card_ls.append(new_card)
	cards["cards"] = card_ls
	
	print (cards)
	
	json_file.seek(0) # go to beginning
	json.dump(cards, json_file)
	json_file.close()

	new_card_filename = new_card["filename"]
	# then write the actual file
	with open("./sgf_files/" + new_card_filename
		+ ".sgf", "wb") as f:
		f.write(sgf_game.serialise()) 