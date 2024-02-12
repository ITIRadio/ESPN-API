from urllib.request import urlopen
import json
import sys
import datetime
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN NFL Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. NFL_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. NFL_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Usage: python3 ESPNNFLAPIBoxScores.py YYYYMMDD          Date parameter optional, 1 day allowed only, otherwise get games on current scoreboard
#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def NFL_post_game(game_number):
	
	#Make event API call & transfer to dictionary. Note that the game number, or id, is passed into the def for the API call
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=" + NFL_data_json['events'][game_number]['id']
	NFL_event = urlopen(url_event)
	NFL_event_data_json = json.loads(NFL_event.read())
	
	console = Console()
	
	try:
		team_stats = Table(box=None, header_style="default")
		team_stats.add_column("")
		team_stats.add_column(NFL_event_data_json['boxscore']['teams'][0]['team']['abbreviation'], justify="right")
		team_stats.add_column(NFL_event_data_json['boxscore']['teams'][1]['team']['abbreviation'], justify="right")
		team_stats.add_row("1st Downs", NFL_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'])
		team_stats.add_row("Rushing", NFL_event_data_json['boxscore']['teams'][0]['statistics'][16]['displayValue'] + "-" + NFL_event_data_json['boxscore']['teams'][0]['statistics'][15]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][16]['displayValue'] + "-" + NFL_event_data_json['boxscore']['teams'][1]['statistics'][15]['displayValue'])
		team_stats.add_row("Passing", NFL_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue'])
		team_stats.add_row("Passing Yds", NFL_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'])
		team_stats.add_row("Total Yds", NFL_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'])
		team_stats.add_row("Had Intercepted", NFL_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'])
		team_stats.add_row("Fumbles Lost", NFL_event_data_json['boxscore']['teams'][0]['statistics'][21]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][21]['displayValue'])
		team_stats.add_row("Sacked-Yds Lost", NFL_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue'])
		team_stats.add_row("3rd Down Conversions", NFL_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue'])
		team_stats.add_row("4th Down Conversions", NFL_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue'])
		team_stats.add_row("Penalties", NFL_event_data_json['boxscore']['teams'][0]['statistics'][19]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][19]['displayValue'])
		team_stats.add_row("Total Plays", NFL_event_data_json['boxscore']['teams'][0]['statistics'][6]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][6]['displayValue'])
		team_stats.add_row("Time of Possession", NFL_event_data_json['boxscore']['teams'][0]['statistics'][24]['displayValue'], NFL_event_data_json['boxscore']['teams'][1]['statistics'][24]['displayValue'])
	except:
		team_stats = ""

	home_passing = " Passing: "
	for player in range(0, 3):
		try:
			home_passing = home_passing + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0] + ", " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4] + " Int, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][6] + " Rtg, "  
		except IndexError:
			continue
	home_passing = home_passing[:-2]   #Strip last comma & space
	
	home_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			home_rushing = home_rushing + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	home_rushing = home_rushing[:-2]
	
	home_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			home_receiving = home_receiving + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4] + " Long, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][5] + " Tgt, "
		except IndexError:
			continue
	home_receiving = home_receiving[:-2]
	
	home_punting = " Punting: "
	for player in range(0, 10):
		try:
			home_punting = home_punting + NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][0] + " Punt, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][2] + " Avg, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][5] + " Long, "
		except IndexError:
			continue
	if home_punting == " Punting: ":
		home_punting = home_punting + "None"
	else:
		home_punting = home_punting[:-2]
	
	home_punt_return = " Punt Returns: "
	for player in range(0, 10):
		try:
			home_punt_return = home_punt_return + NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][0] + " Return, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if home_punt_return == " Punt Returns: ":
		home_punt_return = home_punt_return + "None"
	else:
		home_punt_return = home_punt_return[:-2]
	
	home_kick_return = " Kick Returns: "
	for player in range(0, 10):
		try:
			home_kick_return = home_kick_return + NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][0] + " Return, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if home_kick_return == " Kick Returns: ":
		home_kick_return = home_kick_return + "None"
	else:
		home_kick_return = home_kick_return[:-2]
	
	home_interceptions = " Interceptions: "
	for player in range(0, 10):
		try:
			home_interceptions = home_interceptions + NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][0] + " Interception, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][1] + " Yds, "
		except IndexError:
			continue
	if home_interceptions == " Interceptions: ":
		home_interceptions = home_interceptions + "None"
	else:
		home_interceptions = home_interceptions[:-2]
	
	try:
		home_def_stats = Table(box=None, header_style="default")
		home_def_stats.add_column("Defensive Stats")
		home_def_stats.add_column("Tkls", justify="right")
		home_def_stats.add_column("Solo", justify="right")
		home_def_stats.add_column("Sacks", justify="right")
		home_def_stats.add_column("TFL", justify="right")
		home_def_stats.add_column("PD", justify="right")
		home_def_stats.add_column("QB Hit", justify="right")
		home_def_stats.add_column("TDs", justify="right")
		for player in range (0, 50):
			try:
				home_def_stats.add_row(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['athlete']['displayName'], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][0], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][1], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][2], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][3], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][4], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][5], NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][6])
			except IndexError:
				continue
	except:
		home_def_stats = ""

	visitor_passing = " Passing: "
	for player in range(0, 3):
		try:
			visitor_passing = visitor_passing + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0] + ", " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4] + " Int, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][6] + " Rtg, "  
		except IndexError:
			continue
	visitor_passing = visitor_passing[:-2]
	
	visitor_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			visitor_rushing = visitor_rushing + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	visitor_rushing = visitor_rushing[:-2]
	
	visitor_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			visitor_receiving = visitor_receiving + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4] + " Long, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][5] + " Tgt, "
		except IndexError:
			continue
	visitor_receiving = visitor_receiving[:-2]
	
	visitor_punting = " Punting: "
	for player in range(0, 10):
		try:
			visitor_punting = visitor_punting + NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][0] + " Punt, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][2] + " Avg, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][5] + " Long, "
		except IndexError:
			continue
	if visitor_punting == " Punting: ":
		visitor_punting = visitor_punting + "None"
	else:
		visitor_punting = visitor_punting[:-2]
	
	visitor_punt_return = " Punt Returns: "
	for player in range(0, 10):
		try:
			visitor_punt_return = visitor_punt_return + NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][0] + " Return, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if visitor_punt_return == " Punt Returns: ":
		visitor_punt_return = visitor_punt_return + "None"
	else:
		visitor_punt_return = visitor_punt_return[:-2]
	
	visitor_kick_return = " Kick Returns: "
	for player in range(0, 10):
		try:
			visitor_kick_return = visitor_kick_return + NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][0] + " Return, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if visitor_kick_return == " Kick Returns: ":
		visitor_kick_return = visitor_kick_return + "None"
	else:
		visitor_kick_return = visitor_kick_return[:-2]
	
	visitor_interceptions = " Interceptions: "
	for player in range(0, 10):
		try:
			visitor_interceptions = visitor_interceptions + NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][0] + " Interception, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][1] + " Yds, "
		except IndexError:
			continue
	if visitor_interceptions == " Interceptions: ":
		visitor_interceptions = visitor_interceptions + "None"
	else:
		visitor_interceptions = visitor_interceptions[:-2]

	try:
		visitor_def_stats = Table(box=None, header_style="default")
		visitor_def_stats.add_column("Defensive Stats")
		visitor_def_stats.add_column("Tkls", justify="right")
		visitor_def_stats.add_column("Solo", justify="right")
		visitor_def_stats.add_column("Sacks", justify="right")
		visitor_def_stats.add_column("TFL", justify="right")
		visitor_def_stats.add_column("PD", justify="right")
		visitor_def_stats.add_column("QB Hit", justify="right")
		visitor_def_stats.add_column("TDs", justify="right")
		for player in range (0, 50):
			try:
				visitor_def_stats.add_row(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['athlete']['displayName'], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][0], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][1], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][2], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][3], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][4], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][5], NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][6])
			except IndexError:
				continue
	except:
		visitor_def_stats = ""

	try:
		home_qtrs = str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][0]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][1]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][2]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][3]['value']))
	except:
		home_qtrs = ""

	try:
		home_ot = str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][4]['value']))
	except:
		home_ot = " "
	if home_ot != " ":
		home_qtrs = home_qtrs + " + " + home_ot

	try:
		visitor_qtrs = str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][0]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][1]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][2]['value'])) + " + " + str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][3]['value']))
	except:
		visitor_qtrs = ""

	try:
		visitor_ot = str(int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][4]['value']))
	except:
		visitor_ot = " "
	if visitor_ot != " ":
		visitor_qtrs = visitor_qtrs + " + " +  visitor_ot
	
	scoring_plays = " Scoring Plays:" + "\n "
	for play in range(0,20):
		try:
			scoring_plays = scoring_plays + NFL_event_data_json['scoringPlays'][play]['team']['abbreviation'] + ": " + NFL_event_data_json['scoringPlays'][play]['text'].rstrip().lstrip() + ", Qtr " + str(NFL_event_data_json['scoringPlays'][play]['period']['number']) + ", " + NFL_event_data_json['scoringPlays'][play]['clock']['displayValue'] + "\n "
		except IndexError:
			continue
	if scoring_plays != "Scoring Plays:\n":
		scoring_plays = scoring_plays[:-2]
	
	drives_plays = " Drives & Play-by-play:\n"
	for drive in range(0,50):
		try:
			drives_plays = drives_plays + " " + NFL_event_data_json['drives']['previous'][drive]['team']['abbreviation'] + " Drive: " + NFL_event_data_json['drives']['previous'][drive]['description'] + ", " + NFL_event_data_json['drives']['previous'][drive]['displayResult'] + ":\n"
			for plays in range(0,25):
				try:
					play_down_dist = NFL_event_data_json['drives']['previous'][drive]['plays'][plays]['start']['downDistanceText']
				except:
					play_down_dist = ""
				try:
					play_clock = NFL_event_data_json['drives']['previous'][drive]['plays'][plays]['clock']['displayValue']
				except:
					play_clock = ""
				try:
					play_qtr = NFL_event_data_json['drives']['previous'][drive]['plays'][plays]['period']['number']
				except:
					play_qtr = ""
				if play_clock == "" or play_qtr == "":
					if play_down_dist == "":
						play_status = ""
					else:
						play_status = "(" + play_down_dist + ") "
				else:
					if play_down_dist == "":
						play_status = "(" + play_clock + " - Qtr " + str(play_qtr) + ") "
					else:
						play_status = "(" + play_down_dist + ", " + play_clock + " - Qtr " + str(play_qtr) + ") "
				try:
					drives_plays = drives_plays + "   " + play_status + NFL_event_data_json['drives']['previous'][drive]['plays'][plays]['text'] + "\n"
				except IndexError:
					continue
			drives_plays = drives_plays + "\n"
		except (IndexError, KeyError) as api_bad_data_problem: 
			continue
	if drives_plays != " Drives & Play-by-play:\n":
		drives_plays = drives_plays[:-2]
	else:
		drives_plays = "No play-by-play data available."

	try:
		article = NFL_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)

	stadium = NFL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	visitor = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	game_status = NFL_data_json['events'][game_number]['status']['type']['detail']
	try:
		home_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""	
	try:
		headline = NFL_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
		
	visitor_len = len(visitor+" ("+visitor_record+") "+" "+str(visitor_score))
	home_len = len(home+" ("+home_record+") "+" "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	
	print(visitor, "("+visitor_record+") "+"  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+") "+"  "+home_add_spc, home_score, game_status, stadium)
	if headline != "":
		print (" "+headline)

	print()
	print(" Score by Quarters")
	score_by_qtrs = Table(box=None, header_style="default")
	score_by_qtrs.add_column(NFL_event_data_json['boxscore']['teams'][0]['team']['abbreviation'])
	score_by_qtrs.add_column(visitor_qtrs)
	score_by_qtrs.add_row(NFL_event_data_json['boxscore']['teams'][1]['team']['abbreviation'], home_qtrs)
	console.print(score_by_qtrs)
	print()
	console.print(team_stats)
	print()
	if scoring_plays != "Scoring Plays:\n":
		print(scoring_plays)
	print()
	print(" " + visitor + " Individual Stats:")
	print(visitor_passing)
	print(visitor_rushing)
	print(visitor_receiving)
	print(visitor_punting)
	print(visitor_punt_return)
	print(visitor_kick_return)
	print(visitor_interceptions)
	print()
	console.print(visitor_def_stats)
	print()
	print(" " + home + " Individual Stats:")
	print(home_passing)
	print(home_rushing)
	print(home_receiving)
	print(home_punting)
	print(home_punt_return)
	print(home_kick_return)
	print(home_interceptions)
	print()
	console.print(home_def_stats)

	if article != "":
		print()
		print(article)
	print()
	print(drives_plays)
	print("----------------------------------------------------------------------")
	print()

def NFL_in_progress(game_number):
		
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=" + NFL_data_json['events'][game_number]['id']
	NFL_event = urlopen(url_event)
	NFL_event_data_json = json.loads(NFL_event.read())
	
	try:
		home_team_stats = " " + NFL_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + ": " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][0]['label'] + ", " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][16]['displayValue'] + "-" + NFL_event_data_json['boxscore']['teams'][1]['statistics'][15]['displayValue'] + " Rushing, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue'] + ", " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'] + " Yds Passing, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'] + " Total Yds, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'] + " Int, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][14]['label'] + "\n" + " " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][21]['displayValue'] + " Fum Lost, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue'] + " 3rd Downs, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue'] + " 4th Downs, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][19]['displayValue'] + " Penalties, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][6]['displayValue'] + " Total Plays, " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][24]['displayValue'] + " Possession"
		visitor_team_stats = " " + NFL_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + ": " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][0]['label'] + ", " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][16]['displayValue'] + "-" + NFL_event_data_json['boxscore']['teams'][0]['statistics'][15]['displayValue'] + " Rushing, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue'] + ", " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'] + " Yds Passing, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'] + " Total Yds, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'] + " Int, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][14]['label'] + "\n" + " " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][21]['displayValue'] + " Fum Lost, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue'] + " 3rd Downs, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue'] + " 4th Downs, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][19]['displayValue'] + " Penalties, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][6]['displayValue'] + " Total Plays, " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][24]['displayValue'] + " Possession"
		current_drive = NFL_event_data_json['drives']['current']['description']
		current_drive_possession = NFL_event_data_json['drives']['current']['team']['abbreviation']
	except:
		home_team_stats = ""
		current_drive = ""
		current_drive_possession = ""
		visitor_team_stats = ""
			
	home_passing = " Passing: "
	for player in range(0, 3):
		try:
			home_passing = home_passing + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0] + ", " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4] + " Int, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][6] + " Rtg, "  
		except IndexError:
			continue
	home_passing = home_passing[:-2]
	
	home_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			home_rushing = home_rushing + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	home_rushing = home_rushing[:-2]
	
	home_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			home_receiving = home_receiving + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4] + " Long, " + NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][5] + " Tgt, "
		except IndexError:
			continue
	home_receiving = home_receiving[:-2]

	visitor_passing = " Passing: "
	for player in range(0, 3):
		try:
			visitor_passing = visitor_passing + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0] + ", " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4] + " Int, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][6] + " Rtg, "  
		except IndexError:
			continue
	visitor_passing = visitor_passing[:-2]
	
	visitor_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			visitor_rushing = visitor_rushing + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	visitor_rushing = visitor_rushing[:-2]
	
	visitor_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			visitor_receiving = visitor_receiving + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4] + " Long, " + NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][5] + " Tgt, "
		except IndexError:
			continue
	visitor_receiving = visitor_receiving[:-2]
	
	stadium = NFL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	visitor = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	try:
		home_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""	
	try:
		last_play = NFL_data_json['events'][game_number]['competitions'][0]['situation']['lastPlay']['text']
		home_timeouts = NFL_data_json['events'][game_number]['competitions'][0]['situation']['homeTimeouts']
		visitor_timeouts = NFL_data_json['events'][game_number]['competitions'][0]['situation']['awayTimeouts']
	except:
		last_play = ""
		home_timeouts = ""
		visitor_timeouts = ""
	try:
		down_distance_ball_on = NFL_data_json['events'][game_number]['competitions'][0]['situation']['downDistanceText']
	except:
		down_distance_ball_on = ""
	game_status = NFL_data_json['events'][game_number]['status']['type']['detail']
	
	visitor_len = len(visitor+" ("+visitor_record+") " + str(visitor_timeouts) + " T/O  "+str(visitor_score))
	home_len = len (home+" ("+home_record+") "+str(home_timeouts)+" T/O  "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
		
	print(visitor, "("+visitor_record+") " + str(visitor_timeouts) + " T/O   "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+") "+str(home_timeouts)+" T/O   "+home_add_spc, home_score)
	if down_distance_ball_on != "":
		print (" "+down_distance_ball_on)
	print(" "+game_status, "\n", current_drive_possession+" Ball: "+current_drive, "\n", last_play)
	
	if visitor_team_stats != "":
		print()
		print(visitor_team_stats)
	print(visitor_passing)
	print(visitor_rushing)
	print(visitor_receiving)
	if home_team_stats != "":
		print()
		print(home_team_stats)
	print(home_passing)
	print(home_rushing)
	print(home_receiving)
	print()

def NFL_pre_game(game_number):
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=" + NFL_data_json['events'][game_number]['id']
	NFL_event = urlopen(url_event)
	NFL_event_data_json = json.loads(NFL_event.read())
	
	stadium = NFL_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	game_status = NFL_data_json['events'][game_number]['status']['type']['detail']
	try:
		home_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""	
	try:
		weather = NFL_data_json['events'][game_number]['weather']['displayValue']
		temperature = NFL_data_json['events'][game_number]['weather']['temperature']
	except:
		weather = ""
		temperature = ""
	try:
		broadcast = NFL_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = ""
	try:
		odds = NFL_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
		over_under = NFL_data_json['events'][game_number]['competitions'][0]['odds'][0]['overUnder']
	except:
		odds = ""
		over_under = ""
	
	try:
		visitor_stats = " " + NFL_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + " Stats: "
	except:
		visitor_stats = ""

	for stat in range(0, 10):
		try:
			visitor_stats = visitor_stats + NFL_event_data_json['boxscore']['teams'][0]['statistics'][stat]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][0]['statistics'][stat]['label'] + ", "
		except IndexError:
			pass
	visitor_stats = visitor_stats[:-2]

	try:
		home_stats = " " + NFL_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + " Stats: "
	except:
		home_stats = ""

	for stat in range(0, 10):
		try:
			home_stats = home_stats + NFL_event_data_json['boxscore']['teams'][1]['statistics'][stat]['displayValue'] + " " + NFL_event_data_json['boxscore']['teams'][1]['statistics'][stat]['label'] + ", "
		except IndexError:
			pass
	home_stats = home_stats[:-2]

	visitor_leaders = " "
	try:
		visitor_leaders = visitor_leaders + NFL_event_data_json['leaders'][1]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][1]['leaders'][0]['leaders'][0]['displayValue'] + ", " + NFL_event_data_json['leaders'][1]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][1]['leaders'][1]['leaders'][0]['displayValue'] + ", " + NFL_event_data_json['leaders'][1]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][1]['leaders'][2]['leaders'][0]['displayValue']
	except:
		pass

	home_leaders = " "
	try:
		home_leaders = home_leaders + NFL_event_data_json['leaders'][0]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][0]['leaders'][0]['leaders'][0]['displayValue'] + ", " + NFL_event_data_json['leaders'][0]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][0]['leaders'][1]['leaders'][0]['displayValue'] + ", " + NFL_event_data_json['leaders'][0]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + NFL_event_data_json['leaders'][0]['leaders'][2]['leaders'][0]['displayValue']
	except:
		pass
	
	visitor_injuries = " Injuries: "
	for injury in range(0, 10):
		try:
			visitor_injuries = visitor_injuries + NFL_event_data_json['injuries'][1]['injuries'][injury]['athlete']['fullName'] + "--" + NFL_event_data_json['injuries'][1]['injuries'][injury]['status'] + ", "
		except IndexError:
			pass
	visitor_injuries = visitor_injuries[:-2]

	home_injuries = " Injuries: "
	for injury in range(0, 10):
		try:
			home_injuries = home_injuries + NFL_event_data_json['injuries'][0]['injuries'][injury]['athlete']['fullName'] + "--" + NFL_event_data_json['injuries'][0]['injuries'][injury]['status'] + ", "
		except IndexError:
			pass
	home_injuries = home_injuries[:-2]
		
	home_previous_games = " Previous Games: "
	for game in range(0,5):
		try:
			home_previous_games = home_previous_games + NFL_event_data_json['lastFiveGames'][0]['events'][game]['atVs'] + " " + NFL_event_data_json['lastFiveGames'][0]['events'][game]['opponent']['abbreviation'] + " " + NFL_event_data_json['lastFiveGames'][0]['events'][game]['gameResult'] + " " + NFL_event_data_json['lastFiveGames'][0]['events'][game]['score']
			home_previous_games = home_previous_games[:-1] + ", "
		except IndexError:
			continue
	if home_previous_games != " Previous Games: ":
		home_previous_games = home_previous_games[:-2]

	visitor_previous_games = " Previous Games: "
	for game in range(0,5):
		try:
			visitor_previous_games = visitor_previous_games + NFL_event_data_json['lastFiveGames'][1]['events'][game]['atVs'] + " " + NFL_event_data_json['lastFiveGames'][1]['events'][game]['opponent']['abbreviation'] + " " + NFL_event_data_json['lastFiveGames'][1]['events'][game]['gameResult'] + " " + NFL_event_data_json['lastFiveGames'][1]['events'][game]['score']
			visitor_previous_games = visitor_previous_games[:-1] + ", "
		except IndexError:
			continue
	if visitor_previous_games != " Previous Games: ":
		visitor_previous_games = visitor_previous_games[:-2]

	print(visitor, "("+visitor_record+")", "at", home, "("+home_record+")", "\n", game_status+",", stadium)
	misc_status = " "
	if weather != "" and temperature != "":
		misc_status = misc_status+weather+", "+str(temperature)+", "
	if broadcast != "":
		misc_status = misc_status+broadcast+", "
	if odds != "" and over_under != "":
		misc_status = misc_status+"LINE O/U: "+odds+", "+str(over_under)
	if misc_status != " ":
		print(misc_status)
	print()
	if visitor_stats != "":
		print(visitor_stats)
	if visitor_leaders != " ":
		print(visitor_leaders)
	if visitor_injuries != " Injuries: ":
		print(visitor_injuries)
	if visitor_previous_games != " Previous Games: ":
		print(visitor_previous_games)
	print()
	if home_stats != "":
		print(home_stats)
	if home_leaders != " ":
		print(home_leaders)
	if home_injuries != " Injuries: ":
		print(home_injuries)
	if home_previous_games != " Previous Games: ":
		print(home_previous_games)
	print()

#Mainline

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=" + date_arg + "-" + date_arg
	try:
		game_date = datetime.datetime(int(date_arg[0:4]), int(date_arg[4:6]), int(date_arg[6:8]))     
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	print("----------------------------------------------------------------------")
	print("Games of " + game_date.strftime("%B %-d, %Y"))
	print()
else:
	url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

try:
	NFL_today = urlopen(url)
except:
	print("No games on this date.")
	exit()

NFL_data_json = json.loads(NFL_today.read())

for game in range(0, 20):
	try: 
		game_state = NFL_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			NFL_post_game(game)
		elif game_state == "in":
			NFL_in_progress(game)
		else:
			NFL_pre_game(game)
	except IndexError:
		continue