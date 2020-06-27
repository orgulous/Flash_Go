import json
import datetime

def add_card(filename, date_created, space_level, date_due, date_last_reviewed):

	json_file = open("./json/card_data.json", "r+")
	cards = json.load(json_file)
	
	time = datetime.datetime.now()
	time = time.strftime("%c")	
	
	new_card = {
		"filename": filename,
		"date_created": date_created,
		"space_level" : 0,
		"date_last_reviewed": time,
		"date_due": time
	}
	
	card_ls = cards["cards"]
	card_ls.append(new_card)
	cards["cards"] = card_ls
	
	print (cards)
	
	json_file.seek(0) # go to beginning
	json.dump(cards, json_file)
	json_file.close()

time = datetime.datetime.now()
time = time.strftime("%c")	
add_card("test.sgf", time, 0, time, time)
	
