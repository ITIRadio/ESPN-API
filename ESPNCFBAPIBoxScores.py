from urllib.request import urlopen
import json
import sys
import datetime
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN CFB Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. CFB_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. CFB_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Usage: python3 ESPNCFBAPIBoxScores.py YYYYMMDD
#Date parameter is optional, 1 date allowed only
#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def CFB_post_game(game_number):
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())
	
	console = Console()
	
	try:
		team_stats = Table(box=None, header_style="default")
		team_stats.add_column("")
		team_stats.add_column(CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'], justify="right")
		team_stats.add_column(CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'], justify="right")
		team_stats.add_row("1st Downs", CFB_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'])
		team_stats.add_row("Rushing", CFB_event_data_json['boxscore']['teams'][0]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'])
		team_stats.add_row("Passing", CFB_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue'])
		team_stats.add_row("Passing Yds", CFB_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue'])
		team_stats.add_row("Total Yds", CFB_event_data_json['boxscore']['teams'][0]['statistics'][3]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][3]['displayValue'])
		team_stats.add_row("Had Intercepted", CFB_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'])
		team_stats.add_row("Fumbles Lost", CFB_event_data_json['boxscore']['teams'][0]['statistics'][12]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][12]['displayValue'])
		team_stats.add_row("3rd Down Conversions", CFB_event_data_json['boxscore']['teams'][0]['statistics'][1]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][1]['displayValue'])
		team_stats.add_row("4th Down Conversions", CFB_event_data_json['boxscore']['teams'][0]['statistics'][2]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][2]['displayValue'])
		team_stats.add_row("Penalties", CFB_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'])
		team_stats.add_row("Time of Possession", CFB_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue'], CFB_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue'])
	except:
		team_stats = ""
	
	home_passing = " Passing: "
	for player in range(0, 3):
		try:
			home_passing = home_passing + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0] + ", " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4] + " Int, "
		except IndexError:
			continue
	if home_passing != " Passing: ":
		home_passing = home_passing[:-2]
	
	home_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			home_rushing = home_rushing + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	if home_rushing != " Rushing: ":
		home_rushing = home_rushing[:-2]
	
	home_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			home_receiving = home_receiving + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4] + " Long, "
		except IndexError:
			continue
	if home_receiving != " Receiving: ":
		home_receiving = home_receiving[:-2]

	home_punting = " Punting: "
	for player in range(0, 10):
		try:
			home_punting = home_punting + CFB_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][0] + " Punt, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][2] + " Avg, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][5] + " Long, "
		except IndexError:
			continue
	if home_punting == " Punting: ":
		home_punting = home_punting + "None"
	else:
		home_punting = home_punting[:-2]
	
	home_punt_return = " Punt Returns: "
	for player in range(0, 10):
		try:
			home_punt_return = home_punt_return + CFB_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][0] + " Return, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if home_punt_return == " Punt Returns: ":
		home_punt_return = home_punt_return + "None"
	else:
		home_punt_return = home_punt_return[:-2]
	
	home_kick_return = " Kick Returns: "
	for player in range(0, 10):
		try:
			home_kick_return = home_kick_return + CFB_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][0] + " Return, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if home_kick_return == " Kick Returns: ":
		home_kick_return = home_kick_return + "None"
	else:
		home_kick_return = home_kick_return[:-2]
	
	home_interceptions = " Interceptions: "
	for player in range(0, 10):
		try:
			home_interceptions = home_interceptions + CFB_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][0] + " Interception, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][1] + " Yds, "
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
		home_def_stats.add_column("QB Hurries", justify="right")
		home_def_stats.add_column("TDs", justify="right")
		for player in range (0, 50):
			try:
				home_def_stats.add_row(CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['athlete']['displayName'], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][0], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][1], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][2], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][3], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][4], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][5], CFB_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][6])
			except IndexError:
				continue
	except:
		home_def_stats = ""

	visitor_passing = " Passing: "
	for player in range(0, 3):
		try:
			visitor_passing = visitor_passing + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0] + ", " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4] + " Int, "
		except IndexError:
			continue
	if visitor_passing != " Passing: ":
		visitor_passing = visitor_passing[:-2]
	
	visitor_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			visitor_rushing = visitor_rushing + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	if visitor_rushing != " Rushing: ":
		visitor_rushing = visitor_rushing[:-2]
	
	visitor_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			visitor_receiving = visitor_receiving + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4] + " Long, "
		except IndexError:
			continue
	if visitor_receiving != " Receiving: ":
		visitor_receiving = visitor_receiving[:-2]

	visitor_punting = " Punting: "
	for player in range(0, 10):
		try:
			visitor_punting = visitor_punting + CFB_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][0] + " Punt, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][2] + " Avg, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][5] + " Long, "
		except IndexError:
			continue
	if visitor_punting == " Punting: ":
		visitor_punting = visitor_punting + "None"
	else:
		visitor_punting = visitor_punting[:-2]
	
	visitor_punt_return = " Punt Returns: "
	for player in range(0, 10):
		try:
			visitor_punt_return = visitor_punt_return + CFB_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][0] + " Return, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if visitor_punt_return == " Punt Returns: ":
		visitor_punt_return = visitor_punt_return + "None"
	else:
		visitor_punt_return = visitor_punt_return[:-2]
	
	visitor_kick_return = " Kick Returns: "
	for player in range(0, 10):
		try:
			visitor_kick_return = visitor_kick_return + CFB_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][0] + " Return, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][3] + " Long, "
		except IndexError:
			continue
	if visitor_kick_return == " Kick Returns: ":
		visitor_kick_return = visitor_kick_return + "None"
	else:
		visitor_kick_return = visitor_kick_return[:-2]
	
	visitor_interceptions = " Interceptions: "
	for player in range(0, 10):
		try:
			visitor_interceptions = visitor_interceptions + CFB_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][0] + " Interception, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][1] + " Yds, "
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
		visitor_def_stats.add_column("QB Hurries", justify="right")
		visitor_def_stats.add_column("TDs", justify="right")
		for player in range (0, 50):
			try:
				visitor_def_stats.add_row(CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['athlete']['displayName'], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][0], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][1], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][2], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][3], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][4], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][5], CFB_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][6])
			except IndexError:
				continue
	except:
		visitor_def_stats = ""

	drives_plays = " Drives & Play-by-play:\n"
	for drive in range(0,50):
		try:
			drives_plays = drives_plays + " " + CFB_event_data_json['drives']['previous'][drive]['team']['abbreviation'] + " Drive: " + CFB_event_data_json['drives']['previous'][drive]['description'] + ", " + CFB_event_data_json['drives']['previous'][drive]['displayResult'] + ":\n"
			for plays in range(0,25):
				try:
					drives_plays = drives_plays + "   " + CFB_event_data_json['drives']['previous'][drive]['plays'][plays]['text'] + "\n"
				except IndexError:
					continue
			drives_plays = drives_plays + "\n"
		except (IndexError, KeyError) as api_bad_data_problem:
			continue
	if drives_plays != " Drives & Play-by-play:\n":
		drives_plays = drives_plays[:-2]
	else:
		drives_plays = "No play-by-play data available."

	home_qtrs = ""
	visitor_qtrs = ""
	
	for qtr in range(0, 12):
		try:
			home_qtrs = home_qtrs + str(int(CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if home_qtrs != "":
		home_qtrs = home_qtrs[:-3]
		
	for qtr in range(0, 12):
		try:
			visitor_qtrs = visitor_qtrs + str(int(CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if visitor_qtrs != "":
		visitor_qtrs = visitor_qtrs[:-3]
	
	scoring_plays = " Scoring Plays:" + "\n "
	for play in range(0,20):
		try:
			scoring_plays = scoring_plays + CFB_event_data_json['scoringPlays'][play]['team']['abbreviation'] + ": " + CFB_event_data_json['scoringPlays'][play]['text'].rstrip().lstrip() + ", Qtr " + str(CFB_event_data_json['scoringPlays'][play]['period']['number']) + ", " + CFB_event_data_json['scoringPlays'][play]['clock']['displayValue'] + "\n "
		except IndexError:
			continue
	if scoring_plays != "Scoring Plays:\n":
		scoring_plays = scoring_plays[:-2]

	stadium = CFB_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	home_score = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	visitor = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	visitor_score = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	game_status = CFB_data_json['events'][game_number]['status']['type']['detail']	
	try:
		notes = CFB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""
	try:
		headline = CFB_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	try:
		home_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
	except:
		home_rank = 99
	try:
		visitor_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		visitor_rank = 99
	if home_rank == 99:
		home_rank = ""
	else:
		home_rank = ", #"+str(home_rank)
	if visitor_rank == 99:
		visitor_rank = ""
	else:
		visitor_rank = ", #"+str(visitor_rank)
	try:
		visitor_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][3]['summary']
	except:
		visitor_conf_record = "0-0"
	try:
		home_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][3]['summary']
	except:
		home_conf_record = "0-0"
	
	try:
		article = CFB_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)
		
	visitor_len = len(visitor+" ("+visitor_record+", "+visitor_conf_record+visitor_rank+") "+str(visitor_score))
	home_len = len(home+" ("+home_record+", "+home_conf_record+home_rank+") "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	
	print(visitor, "("+visitor_record+", "+visitor_conf_record+visitor_rank+") "+"  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+", "+home_conf_record+home_rank+") "+"  "+home_add_spc, home_score, game_status, stadium)
	if notes != "":
		print(" "+notes)
	if headline != "":
		print (" "+headline)
	
	print()
	print(" Score by Quarters")
	score_by_qtrs = Table(box=None, header_style="default")
	score_by_qtrs.add_column(CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'])
	score_by_qtrs.add_column(visitor_qtrs)
	score_by_qtrs.add_row(CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'], home_qtrs)
	console.print(score_by_qtrs)
	print()
	console.print(team_stats)
	print()
	if scoring_plays != "Scoring Plays:\n":
		print(scoring_plays)
	print()
	print(" " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + " Individual Stats:")
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
	print(" " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + " Individual Stats:")
	print(home_passing)
	print(home_rushing)
	print(home_receiving)
	print(home_punting)
	print(home_punt_return)
	print(home_kick_return)
	print(home_interceptions)
	print()
	console.print(home_def_stats)
	print()
	if article != "":
		print(article)
		print()
	print(drives_plays)
	print("----------------------------------------------------------------------")
	print()

def CFB_in_progress(game_number):
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())
	
	try:
		home_team_stats = " " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + ": " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][0]['label'] + ", " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'] + " Rushing, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue'] + ", " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue'] + " Yds Passing, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][3]['displayValue'] + " Total Yds, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'] + " Int, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][12]['displayValue'] + " Fum Lost, " + "\n " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][1]['displayValue'] + " 3rd Downs, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][2]['displayValue'] + " 4th Downs, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'] + " Penalties, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue'] + " Possession"
		visitor_team_stats = " " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + ": " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][0]['label'] + ", " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'] + " Rushing, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue'] + ", " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue'] + " Yds Passing, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][3]['displayValue'] + " Total Yds, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'] + " Int, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][12]['displayValue'] + " Fum Lost, " + "\n " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][1]['displayValue'] + " 3rd Downs, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][2]['displayValue'] + " 4th Downs, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'] + " Penalties, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue'] + " Possession"
		current_drive = CFB_event_data_json['drives']['current']['description']
		current_drive_possession = CFB_event_data_json['drives']['current']['team']['abbreviation']
	except:
		home_team_stats = ""
		current_drive = ""
		current_drive_possession = ""
		visitor_team_stats = ""
	
	home_passing = " Passing: "
	for player in range(0, 3):
		try:
			home_passing = home_passing + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0] + ", " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4] + " Int, "
		except IndexError:
			continue
	if home_passing != " Passing: ":
		home_passing = home_passing[:-2]
	
	home_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			home_rushing = home_rushing + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	if home_rushing != " Rushing: ":
		home_rushing = home_rushing[:-2]
	
	home_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			home_receiving = home_receiving + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4] + " Long, "
		except IndexError:
			continue
	if home_receiving != " Receiving: ":
		home_receiving = home_receiving[:-2]

	visitor_passing = " Passing: "
	for player in range(0, 3):
		try:
			visitor_passing = visitor_passing + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0] + ", " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4] + " Int, "
		except IndexError:
			continue
	if visitor_passing != " Passing: ":
		visitor_passing = visitor_passing[:-2]
	
	visitor_rushing = " Rushing: "
	for player in range(0, 7):
		try:
			visitor_rushing = visitor_rushing + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0] + " Carries, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4] + " Long, "  
		except IndexError:
			continue
	if visitor_rushing != " Rushing: ":
		visitor_rushing = visitor_rushing[:-2]
	
	visitor_receiving = " Receiving: "
	for player in range(0, 10):
		try:
			visitor_receiving = visitor_receiving + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName'] + " " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0] + " Receptions, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][1] + " Yds, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][3] + " TD, " + CFB_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4] + " Long, "
		except IndexError:
			continue
	if visitor_receiving != " Receiving: ":
		visitor_receiving = visitor_receiving[:-2]

	stadium = CFB_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	home_score = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	visitor = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	visitor_score = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	try:
		last_play = CFB_data_json['events'][game_number]['competitions'][0]['situation']['lastPlay']['text']
		home_timeouts = CFB_data_json['events'][game_number]['competitions'][0]['situation']['homeTimeouts']
		visitor_timeouts = CFB_data_json['events'][game_number]['competitions'][0]['situation']['awayTimeouts']
	except:
		last_play = ""
		home_timeouts = ""
		visitor_timeouts = ""
	try:
		down_distance_ball_on = CFB_data_json['events'][game_number]['competitions'][0]['situation']['downDistanceText']
	except:
		down_distance_ball_on = ""
	game_status = CFB_data_json['events'][game_number]['status']['type']['detail']
	try:
		notes = CFB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""
	try:
		home_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
	except:
		home_rank = 99
	try:
		visitor_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		visitor_rank = 99
	if home_rank == 99:
		home_rank = ""
	else:
		home_rank = ", #"+str(home_rank)
	if visitor_rank == 99:
		visitor_rank = ""
	else:
		visitor_rank = ", #"+str(visitor_rank)
	try:
		visitor_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][3]['summary']
	except:
		visitor_conf_record = "0-0"
	try:
		home_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][3]['summary']
	except:
		home_conf_record = "0-0"

	visitor_len = len(visitor+" ("+visitor_record+", "+visitor_conf_record+visitor_rank+") " + str(visitor_timeouts) + " T/O  "+str(visitor_score))
	home_len = len (home+" ("+home_record+", "+home_conf_record+home_rank+") "+str(home_timeouts)+" T/O  "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	
	print(visitor, "("+visitor_record+", "+visitor_conf_record+visitor_rank+") " + str(visitor_timeouts) + " T/O   "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+", "+home_conf_record+home_rank+") "+str(home_timeouts)+" T/O   "+home_add_spc, home_score)
	if down_distance_ball_on != "":
		print (" "+down_distance_ball_on)
	print(" "+game_status, "\n", current_drive_possession+" Ball: "+current_drive, "\n", last_play)
	if notes != "":
		print(" " + notes)
	
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

def CFB_pre_game(game_number):
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())
	
	stadium = CFB_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	
	visitor = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	
	game_status = CFB_data_json['events'][game_number]['status']['type']['detail']
	try:
		home_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""
	try:
		home_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
	except:
		home_rank = 99
	try:
		visitor_rank = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		visitor_rank = 99
	if home_rank == 99:
		home_rank = ""
	else:
		home_rank = ", #"+str(home_rank)
	if visitor_rank == 99:
		visitor_rank = ""
	else:
		visitor_rank = ", #"+str(visitor_rank)
	try:
		visitor_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][3]['summary']
	except:
		visitor_conf_record = "0-0"
	try:
		home_conf_record = CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][3]['summary']
	except:
		home_conf_record = "0-0"
	try:
		weather = CFB_data_json['events'][game_number]['weather']['displayValue']
		temperature = CFB_data_json['events'][game_number]['weather']['temperature']
	except:
		weather = ""
		temperature = ""
	try:
		broadcast = CFB_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = ""
	try:
		odds = CFB_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
		over_under = CFB_data_json['events'][game_number]['competitions'][0]['odds'][0]['overUnder']
	except:
		odds = ""
		over_under = ""
	try:
		notes = CFB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""
	
	try:
		visitor_stats = " " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + " Stats: "
	except:
		visitor_stats = ""

	for stat in range(0, 10):
		try:
			visitor_stats = visitor_stats + CFB_event_data_json['boxscore']['teams'][0]['statistics'][stat]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][stat]['label'] + ", "
		except IndexError:
			pass
	if visitor_stats != " " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + " Stats: ":
		visitor_stats = visitor_stats[:-2]
	else:
		visitor_stats = " " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + " Stats: "

	try:
		home_stats = " " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + " Stats: "
	except:
		home_stats = ""

	for stat in range(0, 10):
		try:
			home_stats = home_stats + CFB_event_data_json['boxscore']['teams'][1]['statistics'][stat]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][stat]['label'] + ", "
		except IndexError:
			pass
	if home_stats != " " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + " Stats: ":
		home_stats = home_stats[:-2]
	else:
		home_stats = " " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + " Stats: "
	
	#Build visiting & home stat player leaders

	visitor_leaders = " "
	try:
		visitor_leaders = visitor_leaders + CFB_event_data_json['leaders'][1]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][1]['leaders'][0]['leaders'][0]['displayValue'] + ", " + CFB_event_data_json['leaders'][1]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][1]['leaders'][1]['leaders'][0]['displayValue'] + ", " + CFB_event_data_json['leaders'][1]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][1]['leaders'][2]['leaders'][0]['displayValue']
	except:
		pass

	home_leaders = " "
	try:
		home_leaders = home_leaders + CFB_event_data_json['leaders'][0]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][0]['leaders'][0]['leaders'][0]['displayValue'] + ", " + CFB_event_data_json['leaders'][0]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][0]['leaders'][1]['leaders'][0]['displayValue'] + ", " + CFB_event_data_json['leaders'][0]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + CFB_event_data_json['leaders'][0]['leaders'][2]['leaders'][0]['displayValue']
	except:
		pass
		
	home_previous_games = " Previous Games: "
	for game in range(0,5):
		try:
			home_previous_games = home_previous_games + CFB_event_data_json['lastFiveGames'][0]['events'][game]['atVs'] + " " + CFB_event_data_json['lastFiveGames'][0]['events'][game]['opponent']['abbreviation'] + " " + CFB_event_data_json['lastFiveGames'][0]['events'][game]['gameResult'] + " " + CFB_event_data_json['lastFiveGames'][0]['events'][game]['score']
			home_previous_games = home_previous_games[:-1] + ", "
		except IndexError:
			continue
	if home_previous_games != " Previous Games: ":
		home_previous_games = home_previous_games[:-2]

	visitor_previous_games = " Previous Games: "
	for game in range(0,5):
		try:
			visitor_previous_games = visitor_previous_games + CFB_event_data_json['lastFiveGames'][1]['events'][game]['atVs'] + " " + CFB_event_data_json['lastFiveGames'][1]['events'][game]['opponent']['abbreviation'] + " " + CFB_event_data_json['lastFiveGames'][1]['events'][game]['gameResult'] + " " + CFB_event_data_json['lastFiveGames'][1]['events'][game]['score']
			visitor_previous_games = visitor_previous_games[:-1] + ", "
		except IndexError:
			continue
	if visitor_previous_games != " Previous Games: ":
		visitor_previous_games = visitor_previous_games[:-2]

	print(visitor, "("+visitor_record+", "+visitor_conf_record+visitor_rank+")", "at", home, "("+home_record+", "+home_conf_record+home_rank+")", "\n", game_status+",", stadium)
	misc_status = " "
	if weather != "" and temperature != "":
		misc_status = misc_status+weather+", "+str(temperature)+", "
	if broadcast != "":
		misc_status = misc_status+broadcast+", "
	if odds != "" and over_under != "":
		misc_status = misc_status+"LINE O/U: "+odds+", "+str(over_under)
	else:
		misc_status = misc_status+"NO LINE"
	if misc_status != " ":
		print(misc_status)
	if notes != "":
		print(" " + notes)
	print()
	if visitor_stats != "":
		print(visitor_stats)
	if visitor_leaders != " ":
		print(visitor_leaders)
	if visitor_previous_games != " Previous Games: ":
		print(visitor_previous_games)
	print()
	if home_stats != "":
		print(home_stats)
	if home_leaders != " ":
		print(home_leaders)
	if home_previous_games != " Previous Games: ":
		print(home_previous_games)
	print()

#Mainline

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200&dates=" + date_arg + "-" + date_arg
	try:
		game_date = datetime.datetime(int(date_arg[0:4]), int(date_arg[4:6]), int(date_arg[6:8]))     
			#Python sucks...substring is string[beginning_idx:beginning_idx+len], int cast required for month/days starting with 0 for datetime obj
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	print("----------------------------------------------------------------------")
	print("Games of " + game_date.strftime("%B %-d, %Y"))
	print()
else:
	url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200"

try:
	CFB_today = urlopen(url)
except:
	print("No games on this date.")
	exit()

CFB_data_json = json.loads(CFB_today.read())

for game in range(0, 200):
	try: 
		game_state = CFB_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			CFB_post_game(game)
		elif game_state == "in":
			CFB_in_progress(game)
		else:
			CFB_pre_game(game)
	except IndexError:
		continue