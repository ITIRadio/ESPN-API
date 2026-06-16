from urllib.request import urlopen
import json
import sys
from datetime import datetime       #Necessary for date conversion
import pytz                         #Dates are in UTC, though never specified
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN Soccer Scoreboard API to get current list of games;
#For pre-game, output schedule; for in-game, print a summary of stats; for post-game, print game summary & full box score

#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. world_cup_json, the global dictionary for all games, from which a few stats are pulled,
#2. event_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.

#Most Linux distros have json & urllib libraries installed by default; if using another OS, double check. rich will probably require pip installation.
#Usage: python3 ESPNNFLAPIBoxScores.py YYYYMMDD YYYYMMDD
#Due to fewer games being held per day and thus fewer API calls being required, two date parameters are allowed, earliest date first (otherwise
#will return no games). One date parm receives games from that day (US Eastern time), and no parms returns today's games.

def summary(game_number):
	
	console = Console()
	
	json_tz = pytz.timezone("UTC")
	needed_tz = pytz.timezone("US/Eastern")
	game_date = datetime.strptime(world_cup_json['events'][game_number]['competitions'][0]['date'], "%Y-%m-%dT%H:%MZ") #Convert whole json date to datetime obj, but in UTC timezone
	game_date = json_tz.localize(game_date).astimezone(needed_tz)       #Convert game_date datetime obj from UTC to US Eastern
	game_date = game_date.strftime("%B %-d, %Y")    #Convert datetime obj to final string
	
	home = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	home_id = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['id']
	visitor_id = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['id']
	home_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	stadium = world_cup_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + world_cup_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + world_cup_json['events'][game_number]['competitions'][0]['venue']['address']['country']
	if game_state == "post":
		status = world_cup_json['events'][game_number]['competitions'][0]['status']['type']['description']
	else:
		status = world_cup_json['events'][game_number]['competitions'][0]['status']['displayClock']
	try:
		notes = world_cup_json['events'][game_number]['competitions'][0]['altGameNote']
	except:
		notes = ""
	try:           #Optional Later Usage
		attendance = str(world_cup_json['events'][game_number]['competitions'][0]['attendance'])
	except:
		attendance = ""
	home_record = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	visitor_record = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	home_score = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['score'])
	visitor_score = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['score'])
	home_fouls_committed = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue'])
	visitor_fouls_committed = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue'])
	home_corners = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue'])
	visitor_corners = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue'])
	home_possession = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue'] + "%"
	visitor_possession = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue'] + "%"
	home_sog = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue'])
	visitor_sog = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue'])
	home_shot_att = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue'])
	visitor_shot_att = str(world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue'])

	score_box = Table(box=None, header_style="default")
	score_box.add_column(status)
	score_box.add_column("Record")
	score_box.add_column("Goals", justify="right")
	score_box.add_column("Possession", justify="right")
	score_box.add_column("Shots on Goal", justify="right")
	score_box.add_column("Shots Attempted", justify="right")
	score_box.add_column("Fouls Committed", justify="right")
	score_box.add_column("Corners", justify="right")
	score_box.add_row(home, home_record, home_score, home_possession, home_sog, home_shot_att, home_fouls_committed, home_corners)
	score_box.add_row(visitor, visitor_record, visitor_score, visitor_possession, visitor_sog, visitor_shot_att, visitor_fouls_committed, visitor_corners)
	console.print(score_box)
	
	try:
		headline = world_cup_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText'] + "--" + world_cup_json['events'][game_number]['competitions'][0]['headlines'][0]['description']
	except:
		headline = ""
	print(" " + stadium)
	if notes != "":
		print(" " + notes)
	if headline != "":
		print(" " + game_date + ": " + headline)
	else:
		print(" " + game_date)
	print()
	
	game_events = " Game Summary:\n "
	try:
		for game_event_index in range(0, 50):
			try:
				if world_cup_json['events'][game_number]['competitions'][0]['details'][game_event_index]['team']['id'] == home_id:
					game_events = game_events + home_abbr + " -- "
				else:
					game_events = game_events + visitor_abbr + " -- "
				game_events = game_events + world_cup_json['events'][game_number]['competitions'][0]['details'][game_event_index]['clock']['displayValue'] + ": "
				game_events = game_events + world_cup_json['events'][game_number]['competitions'][0]['details'][game_event_index]['type']['text'] + ", "
				game_events = game_events + world_cup_json['events'][game_number]['competitions'][0]['details'][game_event_index]['athletesInvolved'][0]['displayName'] + "\n "
			except IndexError:
				continue
	except:
		game_events = "No game details available."
	game_events = game_events[:-2]
	print(game_events)


def box_score(game_number):
	
	event_id = world_cup_json['events'][game_number]['id']
	event_url = "http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=" + event_id
	world_cup_event = urlopen(event_url)
	event_json = json.loads(world_cup_event.read())
	
	console = Console()
	print()
	home = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	home_id = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['id']
	visitor_id = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['id']
	home_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	
	try:
		home_pass_comp = str(event_json['boxscore']['teams'][0]['statistics'][12]['displayValue']) 
		home_pass_att = str(event_json['boxscore']['teams'][0]['statistics'][13]['displayValue'])
		home_pass_pct = int(event_json['boxscore']['teams'][0]['statistics'][12]['displayValue']) / int(event_json['boxscore']['teams'][0]['statistics'][13]['displayValue'])
		home_pass_pct = f"{home_pass_pct:.1%}"
		home_saves = str(event_json['boxscore']['teams'][0]['statistics'][5]['displayValue'])
		home_offsides = str(event_json['boxscore']['teams'][0]['statistics'][3]['displayValue'])
		home_cross_comp = str(event_json['boxscore']['teams'][0]['statistics'][15]['displayValue'])
		home_cross_att = str(event_json['boxscore']['teams'][0]['statistics'][16]['displayValue'])
		home_long_ball_comp = str(event_json['boxscore']['teams'][0]['statistics'][19]['displayValue'])
		home_long_ball_att = str(event_json['boxscore']['teams'][0]['statistics'][18]['displayValue'])
		home_tackles = str(event_json['boxscore']['teams'][0]['statistics'][23]['displayValue'])
		home_eff_tkls = str(event_json['boxscore']['teams'][0]['statistics'][22]['displayValue'])
		home_blocks = str(event_json['boxscore']['teams'][0]['statistics'][21]['displayValue'])
		home_intercept = str(event_json['boxscore']['teams'][0]['statistics'][25]['displayValue'])
		home_clear = str(event_json['boxscore']['teams'][0]['statistics'][27]['displayValue'])
	
		visitor_pass_comp = str(event_json['boxscore']['teams'][1]['statistics'][12]['displayValue']) 
		visitor_pass_att = str(event_json['boxscore']['teams'][1]['statistics'][13]['displayValue'])
		visitor_pass_pct = int(event_json['boxscore']['teams'][1]['statistics'][12]['displayValue']) / int(event_json['boxscore']['teams'][1]['statistics'][13]['displayValue'])
		visitor_pass_pct = f"{visitor_pass_pct:.1%}"
		visitor_saves = str(event_json['boxscore']['teams'][1]['statistics'][5]['displayValue'])
		visitor_offsides = str(event_json['boxscore']['teams'][1]['statistics'][3]['displayValue'])
		visitor_cross_comp = str(event_json['boxscore']['teams'][1]['statistics'][15]['displayValue'])
		visitor_cross_att = str(event_json['boxscore']['teams'][1]['statistics'][16]['displayValue'])
		visitor_long_ball_comp = str(event_json['boxscore']['teams'][1]['statistics'][19]['displayValue'])
		visitor_long_ball_att = str(event_json['boxscore']['teams'][1]['statistics'][18]['displayValue'])
		visitor_tackles = str(event_json['boxscore']['teams'][1]['statistics'][23]['displayValue'])
		visitor_eff_tkls = str(event_json['boxscore']['teams'][1]['statistics'][22]['displayValue'])
		visitor_blocks = str(event_json['boxscore']['teams'][1]['statistics'][21]['displayValue'])
		visitor_intercept = str(event_json['boxscore']['teams'][1]['statistics'][25]['displayValue'])
		visitor_clear = str(event_json['boxscore']['teams'][1]['statistics'][27]['displayValue'])
	
		stat_box = Table(box=None, header_style="default")
		stat_box.add_column("Team Statistics")
		stat_box.add_column(home_abbr, justify="right")
		stat_box.add_column(visitor_abbr, justify="right")
		stat_box.add_row("Passes Comp./Att.", home_pass_comp + "/" + home_pass_att, visitor_pass_comp + "/" + visitor_pass_att)
		stat_box.add_row("Completion Pct.", home_pass_pct, visitor_pass_pct)
		stat_box.add_row("Saves", home_saves, visitor_saves)
		stat_box.add_row("Offsides", home_offsides, visitor_offsides)
		stat_box.add_row("Crossing Comp./Att.", home_cross_comp + "/" + home_cross_att, visitor_cross_comp + "/" + visitor_cross_att)
		stat_box.add_row("Long Ball Comp./Att.", home_long_ball_comp + "/" + home_long_ball_att, visitor_long_ball_comp + "/" + visitor_long_ball_att)
		stat_box.add_row("Total Tackles", home_tackles, visitor_tackles)
		stat_box.add_row("Effective Tackles", home_eff_tkls, visitor_eff_tkls)
		stat_box.add_row("Blocked Shots", home_blocks, visitor_blocks)
		stat_box.add_row("Interceptions", home_intercept, visitor_intercept)
		stat_box.add_row("Clearances", home_clear, visitor_clear)
		
		console.print(stat_box)
		print()
	except:
		pass
	
	try:                                                      #Home Player Stats
		stat_box = Table(box=None, header_style="default")
		stat_box.add_column(home)
		stat_box.add_column("Pos")
		stat_box.add_column("Fouls", justify="right")
		stat_box.add_column("Fouled", justify="right")
		stat_box.add_column("Ast", justify="right")
		stat_box.add_column("SOG", justify="right")
		stat_box.add_column("Shots", justify="right")
		stat_box.add_column("Replaced")
		
		for plyr in range(0, 30):
			try:
				# Sometimes subs aren't assigned any position (missing ['rosters'][0]['roster'][plyr]['position']['abbreviation']), so check for a starter 1st & add the stat row
				if event_json['rosters'][0]['roster'][plyr]['starter'] == True:
					plyr_name = event_json['rosters'][0]['roster'][plyr]['athlete']['displayName']
					plyr_pos = event_json['rosters'][0]['roster'][plyr]['position']['abbreviation']
					plyr_replaced = ""
					fc = fa = ast = sog = shot = 0
					for stat_nbr in range(0,20):
						try:
							if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FC":
								fc = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FA":
								fa = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "A":
								ast = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SOG":
								sog = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SHOT":
								shot = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
						except IndexError:
							continue
					stat_box.add_row(plyr_name, plyr_pos, fc, fa, ast, sog, shot, plyr_replaced)
				#Not a starter, so position should be SUB
				else:
					if event_json['rosters'][0]['roster'][plyr]['subbedIn'] == True:       #Check to see if got into game
						plyr_name = event_json['rosters'][0]['roster'][plyr]['athlete']['displayName']
						plyr_pos = "SUB"
						plyr_replaced = event_json['rosters'][0]['roster'][plyr]['subbedInFor']['athlete']['displayName'] + " " + event_json['rosters'][0]['roster'][plyr]['plays'][0]['clock']['displayValue']
						fc = fa = ast = sog = shot = 0
						for stat_nbr in range(0,20):
							try:
								if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FC":
									fc = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FA":
									fa = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "A":
									ast = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SOG":
									sog = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SHOT":
									shot = event_json['rosters'][0]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							except IndexError:
								continue
						stat_box.add_row(plyr_name, plyr_pos, fc, fa, ast, sog, shot, plyr_replaced)
			except IndexError:
				continue
		console.print(stat_box)
		print()
	except:
		pass
	
	try:                                                      #Visitor Player Stats
		stat_box = Table(box=None, header_style="default")
		stat_box.add_column(visitor)
		stat_box.add_column("Pos")
		stat_box.add_column("Fouls", justify="right")
		stat_box.add_column("Fouled", justify="right")
		stat_box.add_column("Ast", justify="right")
		stat_box.add_column("SOG", justify="right")
		stat_box.add_column("Shots", justify="right")
		stat_box.add_column("Replaced")
		
		for plyr in range(0, 30):
			try:
				# Sometimes subs aren't assigned any position (missing ['rosters'][1]['roster'][plyr]['position']['abbreviation']), so check for a starter 1st & add the stat row
				if event_json['rosters'][1]['roster'][plyr]['starter'] == True:
					plyr_name = event_json['rosters'][1]['roster'][plyr]['athlete']['displayName']
					plyr_pos = event_json['rosters'][1]['roster'][plyr]['position']['abbreviation']
					plyr_replaced = ""
					fc = fa = ast = sog = shot = 0
					for stat_nbr in range(0,20):
						try:
							if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FC":
								fc = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FA":
								fa = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "A":
								ast = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SOG":
								sog = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SHOT":
								shot = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
						except IndexError:
							continue
					stat_box.add_row(plyr_name, plyr_pos, fc, fa, ast, sog, shot, plyr_replaced)
				#Not a starter, so position should be SUB
				else:
					if event_json['rosters'][1]['roster'][plyr]['subbedIn'] == True:       #Check to see if got into game
						plyr_name = event_json['rosters'][1]['roster'][plyr]['athlete']['displayName']
						plyr_pos = "SUB"
						plyr_replaced = event_json['rosters'][1]['roster'][plyr]['subbedInFor']['athlete']['displayName'] + " " + event_json['rosters'][1]['roster'][plyr]['plays'][0]['clock']['displayValue']
						fc = fa = ast = sog = shot = 0
						for stat_nbr in range(0,20):
							try:
								if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FC":
									fc = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "FA":
									fa = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "A":
									ast = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SOG":
									sog = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
								if event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['shortDisplayName'] == "SHOT":
									shot = event_json['rosters'][1]['roster'][plyr]['stats'][stat_nbr]['displayValue']
							except IndexError:
								continue
						stat_box.add_row(plyr_name, plyr_pos, fc, fa, ast, sog, shot, plyr_replaced)
			except IndexError:
				continue
		console.print(stat_box)
		print()
	except:
		pass
	
	try: 
		article = event_json['article']['story']
		article = re.sub(r'<.*?>', '', article)              # Remove all <> tags
		article = re.sub('\n\n\n\n\n', '\n', article)        # Remove all grouped line feeds
		article = re.sub('\n\n\n\n', '\n', article)
		article = re.sub('\n\n\n', '\n', article)
		article = re.sub('\n\n', '\n', article)
		print(article)
	except:
		pass
	
	try:
		comments = " Commentary:\n "
		for plays in range(0, 300):
			try:
				if event_json['commentary'][plays]['time']['displayValue'] != "":
					comments = comments + event_json['commentary'][plays]['time']['displayValue'] + ": " + event_json['commentary'][plays]['text'] + "\n "
			except IndexError:
				continue
		comments = comments[:-2]
		print(comments)
	except:
		pass

def pre_game(game_number):
	
	home = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	home_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_abbr = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	try:
		home_record = world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	except:
		home_record = ""
	try:
		visitor_record = world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		visitor_record = ""
	status = world_cup_json['events'][game_number]['competitions'][0]['status']['type']['detail']
	stadium = world_cup_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + world_cup_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + world_cup_json['events'][game_number]['competitions'][0]['venue']['address']['country']
	try:
		notes = world_cup_json['events'][game_number]['competitions'][0]['altGameNote']
	except:
		notes = ""
	form = "Last 5 games (latest 1st): "
	try:
		form = form + home_abbr + " " + world_cup_json['events'][game_number]['competitions'][0]['competitors'][0]['form'] + ", " + visitor_abbr + " " + world_cup_json['events'][game_number]['competitions'][0]['competitors'][1]['form']
	except:
		pass
	try:
		odds = world_cup_json['events'][game_number]['competitions'][0]['odds'][0]['details']
	except:
		odds = "Not available"
	print(home + " (" + home_record + ") vs. " + visitor + " (" + visitor_record + ")")
	print(status)
	print(stadium)
	if notes != "":
		print(notes)
	if form != "Last 5 games: ":
		print(form)
	print("Money Line: " + odds)


#Mainline

if len(sys.argv) == 2:
	url = "http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=" + str(sys.argv[1]) + "-" + str(sys.argv[1])
elif len(sys.argv) == 3:
	url = "http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=" + str(sys.argv[1]) + "-" + str(sys.argv[2])
else:
	url = "http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

try:
	world_cup_today = urlopen(url)
except:
	print("Incorrect date format, use YYYYMMDD or YYYYMMDD YYYYMMDD, earlier date first.")
	exit()

world_cup_json = json.loads(world_cup_today.read())

for game in range(0, 100):
	try:
		game_state = world_cup_json['events'][game]['status']['type']['state']
		if game_state == "post":
			summary(game)
			box_score(game)
		elif game_state == "in":
			summary(game)
		else:
			pre_game(game)
		print("--------------------------------------------------------------------------------")
	except IndexError:
		continue


