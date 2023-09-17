from urllib.request import urlopen
import json
import sys
import datetime
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN NHL Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. NHL_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. NHL_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Most Linux distros have json & urllib libraries installed by default; if using another OS, double check.
#Usage: python3 -u ESPNNHLAPIBoxScores.py YYYYMMDD          Date parameter optional, add 2nd date in same format for a date range, otherwise get games on current scoreboard

#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def NHL_post_game(game_number):

	event_id = NHL_data_json['events'][game_number]['id']
	event_url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/summary?event=" + event_id
	NHL_event = urlopen(event_url)
	NHL_event_data_json = json.loads(NHL_event.read())
	
	#Set up rich text printing console, team totals
	console = Console()
	
	home_team_id = NHL_event_data_json['boxscore']['teams'][1]['team']['id']
	visitor_team_id = NHL_event_data_json['boxscore']['teams'][0]['team']['id']
	home_team_abbr = NHL_event_data_json['boxscore']['teams'][1]['team']['abbreviation']
	visitor_team_abbr = NHL_event_data_json['boxscore']['teams'][0]['team']['abbreviation']
	arena = NHL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_record = NHL_event_data_json['header']['competitions'][0]['competitors'][0]['record'][0]['displayValue']
	home_short = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
	visitor = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_record = NHL_event_data_json['header']['competitions'][0]['competitors'][1]['record'][0]['displayValue']
	visitor_short = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	home_team_stats = " " + home_short + " (" + home_record + "): " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][3]['displayValue']) + " Shots on Goal, " + str(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue']) + " Save Pct., " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue']) + "/" + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue']) + " Power Plays, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][9]['displayValue']) + " Faceoffs Won, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][12]['displayValue']) + "/" + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue']) + " Penalties, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue']) + " Blocked Shots, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][1]['displayValue']) + " Hits, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][2]['displayValue']) + " Takeaways, " + str(NHL_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue']) + " Giveaways"
	visitor_team_stats = " " + visitor_short + " (" + visitor_record + "): " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][3]['displayValue']) + " Shots on Goal, " + str(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue']) + " Save Pct., "  + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue']) + "/" + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue']) + " Power Plays, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][9]['displayValue']) + " Faceoffs Won, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][12]['displayValue']) + "/" + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue']) + " Penalties, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue']) + " Blocked Shots, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][1]['displayValue']) + " Hits, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][2]['displayValue']) + " Takeaways, " + str(NHL_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue']) + " Giveaways"

	#Set up player stat lines
	home_player_stats = Table(box=None, header_style="default")
	home_player_stats.add_column("")
	home_player_stats.add_column("Shots", justify="right")
	home_player_stats.add_column("+/-", justify="right")
	home_player_stats.add_column("Time on Ice", justify="right")
	home_player_stats.add_column("Miss", justify="right")
	home_player_stats.add_column("Blks", justify="right")
	home_player_stats.add_column("Hits", justify="right")
	home_player_stats.add_column("F/O W-L", justify="right")
	home_player_stats.add_column("Tk", justify="right")
	home_player_stats.add_column("Gv", justify="right")
	
	for player in range(0, 20): #Forwards
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_shots = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][12])
			player_pen = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][19])
			player_pim = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][20])
			player_plusminus = int(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3])
			if player_plusminus > 0:
				player_plusminus = "+" + str(player_plusminus)
			else:
				player_plusminus = str(player_plusminus)
			player_toi = NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4]
			player_goals = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][9])
			player_ytdgoals = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][10])   #Future Use
			player_ast = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][11])
			player_miss = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][13])
			player_blks = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0])
			player_hits = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1])
			player_fow = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][15])
			player_fol = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][16])
			player_tks = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][2])
			player_gives = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][18])

			home_player_stats.add_row(player_name, player_shots, player_plusminus, player_toi, player_miss, player_blks, player_hits, player_fow + "-" + player_fol, player_tks, player_gives)
			
		except IndexError:
			continue
	for player in range(0, 20): #Defensemen
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['shortName']
			player_shots = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][12])
			player_pen = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][19])
			player_pim = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][20])
			player_plusminus = int(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3])
			if player_plusminus > 0:
				player_plusminus = "+" + str(player_plusminus)
			else:
				player_plusminus = str(player_plusminus)
			player_toi = NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4]
			player_goals = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][9])
			player_ytdgoals = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][10])
			player_ast = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][11])
			player_miss = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][13])
			player_blks = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0])
			player_hits = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1])
			player_fow = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][15])
			player_fol = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][16])
			player_tks = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][2])
			player_gives = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][18])
			
			home_player_stats.add_row(player_name, player_shots, player_plusminus, player_toi, player_miss, player_blks, player_hits, player_fow + "-" + player_fol, player_tks, player_gives)
			
		except IndexError:
			continue
		
	home_team_stats = home_team_stats + "\n Goaltenders: "
	for player in range(0, 5): #Goalies
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['shortName']
			player_saves = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4])
			player_ga = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0])
			player_pct = str(NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][5])
			player_toi = NHL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][9]
			home_team_stats = home_team_stats + player_name + " " + player_saves + " Saves, " + player_ga + " Goals Against, " + player_pct + " Save Percent, " + player_toi + " Time On Ice\n "
		except IndexError:
			continue

	visitor_player_stats = Table(box=None, header_style="default")
	visitor_player_stats.add_column("")
	visitor_player_stats.add_column("Shots", justify="right")
	visitor_player_stats.add_column("+/-", justify="right")
	visitor_player_stats.add_column("Time on Ice", justify="right")
	visitor_player_stats.add_column("Miss", justify="right")
	visitor_player_stats.add_column("Blks", justify="right")
	visitor_player_stats.add_column("Hits", justify="right")
	visitor_player_stats.add_column("F/O W-L", justify="right")
	visitor_player_stats.add_column("Tk", justify="right")
	visitor_player_stats.add_column("Gv", justify="right")
	
	for player in range(0, 20): #Forwards
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_shots = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][12])
			player_pen = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][19])
			player_pim = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][20])
			player_plusminus = int(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3])
			if player_plusminus > 0:
				player_plusminus = "+" + str(player_plusminus)
			else:
				player_plusminus = str(player_plusminus)
			player_toi = NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4]
			player_goals = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][9])
			player_ytdgoals = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][10])
			player_ast = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][11])
			player_miss = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][13])
			player_blks = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0])
			player_hits = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1])
			player_fow = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][15])
			player_fol = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][16])
			player_tks = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][2])
			player_gives = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][18])
			
			visitor_player_stats.add_row(player_name, player_shots, player_plusminus, player_toi, player_miss, player_blks, player_hits, player_fow + "-" + player_fol, player_tks, player_gives)
			
		except IndexError:
			continue
	for player in range(0, 20): #Defensemen
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['shortName']
			player_shots = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][12])
			player_pen = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][19])
			player_pim = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][20])
			player_plusminus = int(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3])
			if player_plusminus > 0:
				player_plusminus = "+" + str(player_plusminus)
			else:
				player_plusminus = str(player_plusminus)
			player_toi = NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4]
			player_goals = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][9])
			player_ytdgoals = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][10])
			player_ast = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][11])
			player_miss = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][13])
			player_blks = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0])
			player_hits = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1])
			player_fow = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][15])
			player_fol = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][16])
			player_tks = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][2])
			player_gives = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][18])
			
			visitor_player_stats.add_row(player_name, player_shots, player_plusminus, player_toi, player_miss, player_blks, player_hits, player_fow + "-" + player_fol, player_tks, player_gives)
			
		except IndexError:
			continue
		
	visitor_team_stats = visitor_team_stats + "\n Goaltenders: "
	for player in range(0, 5): #Goalies
		try:
			try:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['shortName']
			player_saves = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4])
			player_ga = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0])
			player_pct = str(NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][5])
			player_toi = NHL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][9]
			visitor_team_stats = visitor_team_stats + player_name + " " + player_saves + " Saves, " + player_ga + " Goals Against, " + player_pct + " Save Percent, " + player_toi + " Time On Ice\n "
		except IndexError:
			continue
	
    #Build penalty & goal lists
	penalties = " Penalties:\n "
	goals = " Goals:\n "
	for play in range(0,1000):
		try:
			play_type = NHL_event_data_json['plays'][play]['type']['abbreviation']
			play_team_id = NHL_event_data_json['plays'][play]['team']['id']
			if play_team_id == home_team_id:
				play_team_abbr = home_team_abbr
			else:
				play_team_abbr = visitor_team_abbr
			if play_type == "penalty":
				penalties = penalties + NHL_event_data_json['plays'][play]['text'] + " (" + play_team_abbr + ", " + NHL_event_data_json['plays'][play]['period']['displayValue'] + ", " + NHL_event_data_json['plays'][play]['clock']['displayValue'] + ")\n "
			if play_type == "goal":
				goals = goals + NHL_event_data_json['plays'][play]['text'] + " (" + play_team_abbr + ", " + NHL_event_data_json['plays'][play]['period']['displayValue'] + ", " + NHL_event_data_json['plays'][play]['clock']['displayValue'] + ", " + NHL_event_data_json['plays'][play]['strength']['text'] + ")\n "
		except (IndexError, KeyError) as api_bad_data_problem:
			continue

	if penalties == " Penalties: ":
		penalties = " No Penalties."
	else:
		penalties = penalties[:-2]
	if goals == " Goals: ":
		goals = " No Regulation or Overtime Goals."
	else:
		goals = goals[:-2]		

	game_status = NHL_data_json['events'][game_number]['status']['type']['detail']

    #Build shootout log
	if game_status == "Final/SO":
		start_shootout_log = 0
		shootout = " Shootout: "
		for play in range(0,1000):
			try:
				play_text = NHL_event_data_json['plays'][play]['text']
				if start_shootout_log == 1 and play_text[0:15] != "End of Shootout":
					play_team_id = NHL_event_data_json['plays'][play]['team']['id']
					if play_team_id == home_team_id:
						play_team_abbr = home_team_abbr
					else:
						play_team_abbr = visitor_team_abbr
					shootout = shootout + play_text + " (" + play_team_abbr + "), "
				if play_text[0:15] == "End of Shootout":
					start_shootout_log = 0
				if play_text[0:17] == "Start of Shootout":
					start_shootout_log = 1
			except (IndexError, KeyError) as api_bad_data_problem:
				continue
		if shootout == " Shootout: ":
			shootout = " No Shootout log available."
		else:
			shootout = shootout[:-2]

	home_periods = ""
	visitor_periods = ""
	for period in range(0, 12):
		try:
			home_periods = home_periods + str(int(NHL_event_data_json['header']['competitions'][0]['competitors'][0]['linescores'][period]['displayValue'])) + " + "
		except IndexError:
			continue
	if home_periods != "":                         #Remove extra + at end
		home_periods = home_periods[:-3]
	for period in range(0, 12):
		try:
			visitor_periods = visitor_periods + str(int(NHL_event_data_json['header']['competitions'][0]['competitors'][1]['linescores'][period]['displayValue'])) + " + "
		except IndexError:
			continue
	if visitor_periods != "":
		visitor_periods = visitor_periods[:-3]

	try:
		headline = NHL_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	try:
		notes = NHL_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NHL_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass
	
	try:
		article = NHL_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)

	visitor_len = len(visitor)
	home_len = len(home)
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)

	#Print box score
	print(visitor + "  " + visitor_add_spc + visitor_periods + "   " + visitor_score)
	print(home + "  " + home_add_spc + home_periods + "   " + home_score, game_status, arena)
	if notes != "":
		print(notes)
	if headline != "":
		print(headline + "\n")
	else:
		print()
	
	print(goals)
	print()
	print(penalties)
	if game_status == "Final/SO":
		print("\n" + shootout)
	print()

	print(visitor_team_stats)
	console.print(visitor_player_stats)
	print()
	print(home_team_stats)
	console.print(home_player_stats)
	print()

	if article != "":
		print(article + "\n")

def NHL_in_progress(game_number):

	arena = NHL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_record = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	visitor = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_record = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	try:
		headline = NHL_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	try:
		notes = NHL_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NHL_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass		 
	game_status = NHL_data_json['events'][game_number]['status']['type']['detail']
	try:
		broadcast = NHL_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	home_shots = str(int(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']) + int(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']))
	visitor_shots = str(int(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']) + int(NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']))

	visitor_len = len(visitor+" ("+visitor_record+") "+visitor_score)
	home_len = len(home+" ("+home_record+") "+home_score)
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	print(visitor, "("+visitor_record+")  "+visitor_add_spc, visitor_score + "     " + visitor_shots + " Shots on Goal")
	print(home, "("+home_record+")  "+home_add_spc, home_score + "     " + home_shots + " Shots on Goal")
	print(game_status)
	print(arena+",", broadcast)
	if notes != "":
		print(notes)
	print()

def NHL_pre_game(game_number):
												 
	arena = NHL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_record = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	visitor = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_record = NHL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	try:
		notes = NHL_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NHL_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass		 
	game_status = NHL_data_json['events'][game_number]['status']['type']['detail']
	try:
		broadcast = NHL_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	try:
		odds = NHL_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
	except:
		odds = ""

	print(visitor, "("+visitor_record+")" + " at " + home, "("+home_record+")")
	print(game_status+",", arena+",", broadcast)
	if notes != "":
		print(notes)
	if odds != "":
		print("Line: " + odds)
	print()									 
												 
#Mainline

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates=" + date_arg + "-" + date_arg
	try:
		game_date = datetime.datetime(int(date_arg[0:4]), int(date_arg[4:6]), int(date_arg[6:8]))     
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	print("----------------------------------------------------------------------")
	print("Games of " + game_date.strftime("%B %-d, %Y"))
	print()
elif len(sys.argv) == 3:
	date1_arg = str(sys.argv[1])
	date2_arg = str(sys.argv[2])
	url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates=" + date1_arg + "-" + date2_arg
	try:
		game1_date = datetime.datetime(int(date1_arg[0:4]), int(date1_arg[4:6]), int(date1_arg[6:8]))     
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	try:
		game2_date = datetime.datetime(int(date2_arg[0:4]), int(date2_arg[4:6]), int(date2_arg[6:8]))     
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	print("----------------------------------------------------------------------")
	print("Games of " + game1_date.strftime("%B %-d, %Y") + " through " + game2_date.strftime("%B %-d, %Y"))
	print()
else:
	url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"

try:
	NHL_today = urlopen(url)
except:
	print("No games on this date, or use earlier date first if entering two dates.")
	exit()

NHL_data_json = json.loads(NHL_today.read())

for game in range(0, 20):
	try:
		game_state = NHL_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			NHL_post_game(game)
		elif game_state == "in":
			NHL_in_progress(game)
		else:
			NHL_pre_game(game)
	except IndexError:
		continue

