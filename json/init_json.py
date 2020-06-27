import datetime
import json

time = datetime.datetime.now()
time = time.strftime("%c")	
	
x = {"meta": None, 
	"cards": [{
		"filename": "null.sgf",
		"date_created": time,
		"space_level" : 0,
		"date_last_reviewed": time,
		"date_due": time
	}]
}


with open('card_data.json', 'w') as outfile:
    json.dump(x, outfile)
