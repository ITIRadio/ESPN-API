from urllib.request import urlopen
import json
import sys
from datetime import datetime
import pytz
import re
from rich.console import Console
from rich.table import Table

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def summary(game_number):
	
	console = Console()
	
	json_tz = pytz.timezone("UTC")
	needed_tz = pytz.timezone("US/Eastern")
	game_date = datetime.strptime(league_scoreboard_json['events'][game_number]['competitions'][0]['date'], "%Y-%m-%dT%H:%MZ") #Convert whole json date to datetime obj, but in UTC timezone
	game_date = json_tz.localize(game_date).astimezone(needed_tz)       #Convert game_date datetime obj from UTC to US Eastern
	game_date = game_date.strftime("%B %-d, %Y")    #Convert datetime obj to final string
	
	home = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	home_id = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['id']
	visitor_id = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['id']
	home_abbr = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_abbr = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	try:
		stadium = league_scoreboard_json['events'][game_number]['competitions'][0]['venue']['fullName']
	except:
		stadium = ""
	try:
		location = league_scoreboard_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + league_scoreboard_json['events'][game_number]['competitions'][0]['venue']['address']['country']
	except:
		location = ""
	if game_state == "post":     # Leave in case of status discrepancy
		status = league_scoreboard_json['events'][game_number]['competitions'][0]['status']['type']['description']
	else:
		status = league_scoreboard_json['events'][game_number]['competitions'][0]['status']['displayClock']
	try:
		notes = league_scoreboard_json['events'][game_number]['competitions'][0]['altGameNote']
	except:
		notes = ""
	try:
		notes = notes + ", " + league_scoreboard_json['events'][game_number]['competitions'][0]['notes'][0]['text']
	except:
		pass
	try:           #Optional Later Usage
		attendance = str(league_scoreboard_json['events'][game_number]['competitions'][0]['attendance'])
	except:
		attendance = ""
	try:
		home_record = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	except:
		home_record = ""
	try:
		visitor_record = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		visitor_record = ""
	home_score = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['score'])
	visitor_score = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['score'])
	home_fouls_committed = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue'])
	visitor_fouls_committed = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue'])
	home_corners = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue'])
	visitor_corners = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue'])
	home_possession = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue'] + "%"
	visitor_possession = league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue'] + "%"
	home_sog = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue'])
	visitor_sog = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue'])
	home_shot_att = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue'])
	visitor_shot_att = str(league_scoreboard_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue'])

	score_box = Table(box=None, header_style="default")
	score_box.add_column(status)
	if home_record != "" and visitor_record != "":
		score_box.add_column("Record")
	score_box.add_column("Goals", justify="right")
	score_box.add_column("Possession", justify="right")
	score_box.add_column("Shots on Goal", justify="right")
	score_box.add_column("Shots Attempted", justify="right")
	score_box.add_column("Fouls Committed", justify="right")
	score_box.add_column("Corners", justify="right")
	if home_record != "" and visitor_record != "":
		score_box.add_row(home, home_record, home_score, home_possession, home_sog, home_shot_att, home_fouls_committed, home_corners)
		score_box.add_row(visitor, visitor_record, visitor_score, visitor_possession, visitor_sog, visitor_shot_att, visitor_fouls_committed, visitor_corners)
	else:
		score_box.add_row(home, home_score, home_possession, home_sog, home_shot_att, home_fouls_committed, home_corners)
		score_box.add_row(visitor, visitor_score, visitor_possession, visitor_sog, visitor_shot_att, visitor_fouls_committed, visitor_corners)
	console.print(score_box)
	
	try:
		headline = league_scoreboard_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText'] + "--" + league_scoreboard_json['events'][game_number]['competitions'][0]['headlines'][0]['description']
	except:
		headline = ""
	if stadium != "" and location != "":
		print(" " + stadium + ", " + location)
	if stadium != "" and location == "":
		print(" " + stadium)
	if stadium == "" and location != "":
		print(" " + location)
	if notes != "":
		print(" " + notes)
	if headline != "":
		print(" " + game_date + ": " + headline)
	else:
		print(" " + game_date)
	print()
	
	game_events = " Game Summary:\n "
	for game_event_index in range(0, 50):
		try:                           #Possible no events or phantom events w/no athletes (didn't occur), add event only if all indexes exist
			event_plyr = league_scoreboard_json['events'][game_number]['competitions'][0]['details'][game_event_index]['athletesInvolved'][0]['displayName']
			event_team_id = league_scoreboard_json['events'][game_number]['competitions'][0]['details'][game_event_index]['team']['id']
			event_time = league_scoreboard_json['events'][game_number]['competitions'][0]['details'][game_event_index]['clock']['displayValue']
			event_text = league_scoreboard_json['events'][game_number]['competitions'][0]['details'][game_event_index]['type']['text']
		except (IndexError, KeyError) as api_bad_data_problem:        #Requires both error cases, on either none or no remaining event, or phantom event
			continue
		event_team_abbr = home_abbr if event_team_id == home_id else visitor_abbr
		game_events = game_events + event_team_abbr + " -- " + event_time + ": " + event_text + ", " + event_plyr + "\n "

	if game_events != " Game Summary:\n ":
		game_events = game_events[:-2]
		print(game_events)


#Mainline

if len(sys.argv) == 3:
	date_arg = str(sys.argv[1])
	league_list_file_name = str(sys.argv[2])
	try:
		game_date = date_arg
		datetime.strptime(game_date, "%Y%m%d")                 # Checks for valid date (strptime overwrites date itself within call)
	except:
		print("Use command format: python3 -u ESPNAPISoccerFinals.py YYYYMMDD League_URL_List.txt using one game day as a parameter and league URL list file must already exist.")
		exit()
	try:
		with open(league_list_file_name) as f:
			league_url_list = f.readlines()
	except:
		print("League URL List file error. Use command format: python3 -u ESPNAPISoccerFinals.py YYYYMMDD League_URL_List.txt using one game day as a parameter and league URL list file must already exist.")
		exit()
else:
	print("Use command format: python3 -u ESPNAPISoccerFinals.py YYYYMMDD League_URL_List.txt using one game day as a parameter and league URL list file must already exist.")
	exit()

for league in league_url_list:
	league = league.strip()
	try:
		league = league + "?dates=" + game_date + "-" + game_date
		league_today = urlopen(league)
	except:
		continue                #Sometimes loads OK with no games but raises unknown exception, has no games anyway so just skip like other inactive leagues
	league_scoreboard_json = json.loads(league_today.read())
	for game in range (0, 50):
		try:
			game_state = league_scoreboard_json['events'][game]['status']['type']['state']
			if game_state == "post":
				summary(game)
			print("--------------------------------------------------------------------------------")
		except IndexError:      #Either out of games that have gone final, or no games in that league on given date, so skip to next league silently
			continue


		