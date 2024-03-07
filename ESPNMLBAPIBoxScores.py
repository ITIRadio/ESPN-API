from urllib.request import urlopen
import json
import sys
import datetime
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN MLB Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. MLB_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. MLB_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Usage: python3 ESPNMLBAPIBoxScores.py YYYYMMDD
#Date parameter is optional, 1 date allowed only
#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def MLB_post_game(game_number):

	url_event = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event=" + MLB_data_json['events'][game_number]['id']
	MLB_event = urlopen(url_event)
	MLB_event_data_json = json.loads(MLB_event.read())
	
	console = Console()

	game_status = MLB_data_json['events'][game_number]['status']['type']['shortDetail']
	stadium = MLB_data_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['state'] + ", A-" + f"{MLB_data_json['events'][game_number]['competitions'][0]['attendance']:,}"
	home = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	home_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	try:
		home_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""
	try:
		headline = MLB_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	try:
		series = MLB_data_json['events'][game_number]['competitions'][0]['series']['summary']
	except:
		series = ""
	try:
		notes = MLB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""
	print()
	print(" " + visitor + " (" + visitor_record + ")" + " vs. " + home + " (" + home_record + "),", stadium)
	series_status = " "
	if notes != "":
		series_status = series_status + notes + ", "
	if series != "":
		series_status = series_status + series
	else:
		series_status = series_status[:-2]
	if series_status != "":                      #If notes & series_blank are blank, series_status becomes blank
		print(series_status)
	if headline != "":
		print(" " + headline)
	if game_status == "Postponed":
		print(" " + game_status)
		print()
		print("----------------------------------------")
		return

	home_score = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_hits = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['hits']
	home_errors = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['errors']
	visitor_score = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_hits = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['hits']
	visitor_errors = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['errors']

	home_inn = ""
	visitor_inn = ""
	for inn in range(0, 20):
		try:
			home_inn = home_inn + str(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][inn]['value'])) + " "
		except (IndexError, KeyError) as EndForLoop:            #If PPD game, necessary to skip inning loop, similar for pitchers/batters
			continue
	for inn in range(0, 20):
		try:
			visitor_inn = visitor_inn + str(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][inn]['value'])) + " "
		except (IndexError, KeyError) as EndForLoop:
			continue

	pitchers_wls = " "
	for pitcher in range(0,3):
		try:
			pitchers_wls = pitchers_wls + MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['abbreviation'] + "-" + MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['athlete']['shortName'] 
			wins = 0
			losses = 0
			saves = 0
			era = 0
			for statistic in range(0,10):
				try:
					check_stat = MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['statistics'][statistic]['abbreviation']
					if check_stat == "W":
						wins = MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['statistics'][statistic]['displayValue']
					elif check_stat == "L":
						losses = MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['statistics'][statistic]['displayValue']
					elif check_stat =="SV":
						saves = MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['statistics'][statistic]['displayValue']
					elif check_stat == "ERA":
						era = MLB_data_json['events'][game_number]['competitions'][0]['status']['featuredAthletes'][pitcher]['statistics'][statistic]['displayValue']
					else:
						pass
				except:
					continue
			pitchers_wls = pitchers_wls + " (" + wins + "-" + losses + ", " + saves + " Sv, " + era + " ERA)\n "
		except (IndexError, KeyError) as NoPitchersAvail:
			continue
	if pitchers_wls != " ":
		pitchers_wls = pitchers_wls[0:-2]

	visitor_batting = Table(box=None, header_style="default")
	visitor_batting.add_column(MLB_event_data_json['boxscore']['teams'][0]['team']['location'], style="default")
	visitor_batting.add_column("Pos", style="default")
	visitor_batting.add_column("AB", justify="right", style="default")
	visitor_batting.add_column("R", justify="right", style="default")
	visitor_batting.add_column("H", justify="right", style="default")
	visitor_batting.add_column("RBI", justify="right", style="default")
	visitor_batting.add_column("BB", justify="right", style="default")
	visitor_batting.add_column("K", justify="right", style="default")
	visitor_batting.add_column("AVG", justify="right", style="default")
	visitor_batting.add_column("OBP", justify="right", style="default")
	visitor_batting.add_column("SLG", justify="right", style="default")
	bat_order = 0
	for batter in range(0,30):
		try:
			next_bat_order = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['batOrder']
			if next_bat_order > bat_order:
				bat_order = next_bat_order
				batter_name = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['athlete']['displayName']
			else:
				batter_name = " " + MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['athlete']['displayName']
			try:                                #Index priming & continue out thru idx 6 ok
				pos = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['positions'][0]['abbreviation']
				for multi_pos in range (1,5):
					try:
						pos = pos + "-" +  MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['positions'][multi_pos]['abbreviation']
					except:
						continue
			except (IndexError, KeyError) as OnePositionOnly:
				pos = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['position']['abbreviation']
			ab = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][1]
			r = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][2]
			h = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][3]
			rbi = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][4]
			bb = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][6]
			k = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][7]
			avg = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][9]
			obp = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][10]
			slg = MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][batter]['stats'][11]
			visitor_batting.add_row(batter_name, pos, str(ab), str(r), str(h), str(rbi), str(bb), str(k), str(avg), str(obp), str(slg))
		except (IndexError, KeyError) as player_issue:
			continue
	visitor_batting.add_row("Totals", "", str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][1]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][2]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][3]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][4]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][6]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][0]['totals'][7]), "", "", "")
	
	home_batting = Table(box=None, header_style="default")
	home_batting.add_column(MLB_event_data_json['boxscore']['teams'][1]['team']['location'], style="default")
	home_batting.add_column("Pos", style="default")
	home_batting.add_column("AB", justify="right", style="default")
	home_batting.add_column("R", justify="right", style="default")
	home_batting.add_column("H", justify="right", style="default")
	home_batting.add_column("RBI", justify="right", style="default")
	home_batting.add_column("BB", justify="right", style="default")
	home_batting.add_column("K", justify="right", style="default")
	home_batting.add_column("AVG", justify="right", style="default")
	home_batting.add_column("OBP", justify="right", style="default")
	home_batting.add_column("SLG", justify="right", style="default")
	bat_order = 0
	for batter in range(0,30):
		try:
			next_bat_order = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['batOrder']
			if next_bat_order > bat_order:
				bat_order = next_bat_order
				batter_name = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['athlete']['displayName']
			else:
				batter_name = " " + MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['athlete']['displayName']
			try:
				pos = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['positions'][0]['abbreviation']
				for multi_pos in range (1,5):
					try:
						pos = pos + "-" +  MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['positions'][multi_pos]['abbreviation']
					except:
						continue
			except (IndexError, KeyError) as OnePositionOnly:
				pos = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['position']['abbreviation']
			ab = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][1]
			r = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][2]
			h = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][3]
			rbi = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][4]
			bb = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][6]
			k = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][7]
			avg = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][9]
			obp = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][10]
			slg = MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][batter]['stats'][11]
			home_batting.add_row(batter_name, pos, str(ab), str(r), str(h), str(rbi), str(bb), str(k), str(avg), str(obp), str(slg))
		except:
			continue
	home_batting.add_row("Totals", "", str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][1]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][2]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][3]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][4]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][6]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][0]['totals'][7]), "", "", "")

	visitor_batting_details = " "
	for detail in range (0,20):
		try:
			visitor_batting_details = visitor_batting_details + MLB_event_data_json['boxscore']['teams'][0]['details'][0]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][0]['details'][0]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	for detail in range (0,20):
		try:
			visitor_batting_details = visitor_batting_details + MLB_event_data_json['boxscore']['teams'][0]['details'][2]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][0]['details'][2]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	for detail in range (0,20):
		try:
			visitor_batting_details = visitor_batting_details + MLB_event_data_json['boxscore']['teams'][0]['details'][3]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][0]['details'][3]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	if visitor_batting_details != " ":
		visitor_batting_details = visitor_batting_details[:-2]

	home_batting_details = " "
	for detail in range (0,20):
		try:
			home_batting_details = home_batting_details + MLB_event_data_json['boxscore']['teams'][1]['details'][0]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][1]['details'][0]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	for detail in range (0,20):
		try:
			home_batting_details = home_batting_details + MLB_event_data_json['boxscore']['teams'][1]['details'][2]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][1]['details'][2]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	for detail in range (0,20):
		try:
			home_batting_details = home_batting_details + MLB_event_data_json['boxscore']['teams'][1]['details'][3]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][1]['details'][3]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	if home_batting_details != " ":
		home_batting_details = home_batting_details[:-2]

	visitor_pitching_details = " "
	for detail in range (0,20):
		try:
			visitor_pitching_details = visitor_pitching_details + MLB_event_data_json['boxscore']['teams'][0]['details'][1]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][0]['details'][1]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	if visitor_pitching_details != " ":
		visitor_pitching_details = visitor_pitching_details[:-2]

	home_pitching_details = " "
	for detail in range (0,20):
		try:
			home_pitching_details = home_pitching_details + MLB_event_data_json['boxscore']['teams'][1]['details'][1]['stats'][detail]['abbreviation'] + "-" + MLB_event_data_json['boxscore']['teams'][1]['details'][1]['stats'][detail]['displayValue'] + "\n "
		except IndexError:
			continue
	if home_pitching_details != " ":
		home_pitching_details = home_pitching_details[:-2]

	visitor_pitching = Table(box=None, header_style="default")
	visitor_pitching.add_column(visitor_short + " Pitching", style="default")
	visitor_pitching.add_column("IP", justify="right", style="default")
	visitor_pitching.add_column("H", justify="right", style="default")
	visitor_pitching.add_column("R", justify="right", style="default")
	visitor_pitching.add_column("ER", justify="right", style="default")
	visitor_pitching.add_column("BB", justify="right", style="default")
	visitor_pitching.add_column("K", justify="right", style="default")
	visitor_pitching.add_column("HR", justify="right", style="default")
	visitor_pitching.add_column("PC-ST", justify="right", style="default")
	visitor_pitching.add_column("ERA", justify="right", style="default")
	visitor_pitching.add_column("PC", justify="right", style="default")		
	for pitcher in range(0,30):
		try:
			pitcher_name = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['athlete']['displayName']
			ip = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][0]
			h = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][1]
			r = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][2]
			er = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][3]
			bb = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][4]
			k = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][5]
			hr = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][6]
			pcst = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][7]
			era = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][8]
			pc = MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][pitcher]['stats'][9]
			visitor_pitching.add_row(pitcher_name, str(ip), str(h), str(r), str(er), str(bb), str(k), str(hr), str(pcst), str(era), str(pc))
		except IndexError:
			continue
	visitor_pitching.add_row("Totals", str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][0]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][1]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][2]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][3]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][4]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][5]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][6]), str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][7]), "", str(MLB_event_data_json['boxscore']['players'][0]['statistics'][1]['totals'][9]))

	home_pitching = Table(box=None, header_style="default")
	home_pitching.add_column(home_short + " Pitching", style="default")
	home_pitching.add_column("IP", justify="right", style="default")
	home_pitching.add_column("H", justify="right", style="default")
	home_pitching.add_column("R", justify="right", style="default")
	home_pitching.add_column("ER", justify="right", style="default")
	home_pitching.add_column("BB", justify="right", style="default")
	home_pitching.add_column("K", justify="right", style="default")
	home_pitching.add_column("HR", justify="right", style="default")
	home_pitching.add_column("PC-ST", justify="right", style="default")
	home_pitching.add_column("ERA", justify="right", style="default")
	home_pitching.add_column("PC", justify="right", style="default")		
	for pitcher in range(0,30):
		try:
			pitcher_name = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['athlete']['displayName']
			ip = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][0]
			h = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][1]
			r = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][2]
			er = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][3]
			bb = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][4]
			k = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][5]
			hr = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][6]
			pcst = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][7]
			era = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][8]
			pc = MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][pitcher]['stats'][9]
			home_pitching.add_row(pitcher_name, str(ip), str(h), str(r), str(er), str(bb), str(k), str(hr), str(pcst), str(era), str(pc))
		except IndexError:
			continue
	home_pitching.add_row("Totals", str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][0]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][1]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][2]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][3]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][4]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][5]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][6]), str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][7]), "", str(MLB_event_data_json['boxscore']['players'][1]['statistics'][1]['totals'][9]))

	plays = " Play-by-play:"
	for play in range(0,2000):
		try:
			if MLB_event_data_json['plays'][play]['type']['type'] == "start-inning":
				plays = plays + "\n " + MLB_event_data_json['plays'][play]['text'] + ": "
			elif MLB_event_data_json['plays'][play]['type']['type'] == "play-result":
				plays = plays + MLB_event_data_json['plays'][play]['text'] + " "
			else:
				pass
		except (IndexError, KeyError) as api_bad_data_problem:
			continue
	if plays == " Play-by-play:":
		plays = "No play-by-play data available."

	try:
		article = MLB_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)
	
	rhe = Table(box=None, header_style="default")
	rhe.add_column(game_status, style="default")
	rhe.add_column("", style="default")
	rhe.add_column("R", justify="right", style="default")
	rhe.add_column("H", justify="right", style="default")
	rhe.add_column("E", justify="right", style="default")
	rhe.add_row(visitor_short, visitor_inn, str(visitor_score), str(visitor_hits), str(visitor_errors))
	rhe.add_row(home_short, home_inn, str(home_score), str(home_hits), str(home_errors))
	
	print()
	console.print(rhe)
	print()
	if pitchers_wls != " ":
		print(pitchers_wls)
		print()
	console.print(visitor_batting)
	print()
	print(visitor_batting_details)
	print()
	console.print(home_batting)
	print()
	print(home_batting_details)
	print()
	console.print(visitor_pitching)
	print()
	print(visitor_pitching_details)
	print()
	console.print(home_pitching)
	print()
	print(home_pitching_details)
	if article != "":
		print()
		print(article)
	print()
	print(plays)
	print("----------------------------------------")

def MLB_in_progress(game_number):

	console = Console()

	stadium = MLB_data_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['state']
	home = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	game_status = MLB_data_json['events'][game_number]['status']['type']['shortDetail']
	home_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	try:
		home_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		home_record = ""
		visitor_record = ""
	try:
		broadcast = ", " + MLB_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = ""
	try:
		series = MLB_data_json['events'][game_number]['competitions'][0]['series']['summary']
	except:
		series = ""
	try:
		notes = MLB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""
	balls = MLB_data_json['events'][game_number]['competitions'][0]['situation']['balls']
	strikes = MLB_data_json['events'][game_number]['competitions'][0]['situation']['strikes']
	outs = MLB_data_json['events'][game_number]['competitions'][0]['situation']['outs']
	home_score = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_hits = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['hits']
	home_errors = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['errors']
	visitor_score = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_hits = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['hits']
	visitor_errors = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['errors']
	
	home_inn = ""
	visitor_inn = ""
	for inn in range(0, 20):
		try:
			home_inn = home_inn + str(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][inn]['value'])) + " + "
		except IndexError:
			continue
	if home_inn != "":
		home_inn = home_inn[:-3]
	for inn in range(0, 20):
		try:
			visitor_inn = visitor_inn + str(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][inn]['value'])) + " + "
		except IndexError:
			continue
	if visitor_inn != "":
		visitor_inn = visitor_inn[:-3]

	on_first_bool = int(MLB_data_json['events'][game_number]['competitions'][0]['situation']['onFirst'])    # In JSON as boolean, so cast T/F to 1/0
	on_second_bool = int(MLB_data_json['events'][game_number]['competitions'][0]['situation']['onSecond'])
	on_third_bool = int(MLB_data_json['events'][game_number]['competitions'][0]['situation']['onThird'])
	if on_first_bool == 1:
		on_first = " 1st"
	else:
		on_first = ""
	if on_second_bool == 1:
		on_second = " 2nd"
	else:
		on_second = ""
	if on_third_bool == 1:
		on_third = " 3rd"
	else:
		on_third = ""
	
	rhe = Table(box=None, header_style="default")
	rhe.add_column(game_status, style="default")
	rhe.add_column("", style="default")
	rhe.add_column("R", justify="right", style="default")
	rhe.add_column("H", justify="right", style="default")
	rhe.add_column("E", justify="right", style="default")
	rhe.add_row(visitor_short, visitor_inn, str(visitor_score), str(visitor_hits), str(visitor_errors))
	rhe.add_row(home_short, home_inn, str(home_score), str(home_hits), str(home_errors))
	
	bso = Table(box=None, header_style="black on white")
	bso.add_column("", style="black on white")
	bso.add_column("", style="black on white")
	bso.add_column("Runners", style="black on white")
	bso.add_row("Balls", str(balls), on_first)
	bso.add_row("Strikes", str(strikes), on_second)
	bso.add_row("Outs", str(outs), on_third)
	
	last_play = " " + MLB_data_json['events'][game_number]['competitions'][0]['situation']['lastPlay']['text']
	try:
		pitcher = " Pitcher: " + MLB_data_json['events'][game_number]['competitions'][0]['situation']['pitcher']['athlete']['displayName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['situation']['pitcher']['summary']
	except:
		pitcher = ""
	try:
		batter = " Batter: " + MLB_data_json['events'][game_number]['competitions'][0]['situation']['batter']['athlete']['displayName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['situation']['batter']['summary']
	except:
		batter = ""
	
	print(" " + visitor + " (" + visitor_record + ")" + " vs. " + home + " (" + home_record + ")")
	print (" " + stadium + broadcast)
	series_status = " "
	if notes != "":
		series_status = series_status + notes + ", "
	if series != "":
		series_status = series_status + series
	else:
		series_status = series_status[:-2]
	if series_status != "":
		print(series_status)
	print()
	console.print(rhe)
	print()
	console.print(bso)
	print()
	print(last_play)
	if pitcher != "":
		print(pitcher)
	if batter != "":
		print(batter)
	print("----------------------------------------")

def MLB_pre_game(game_number):
	
	stadium = MLB_data_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['venue']['address']['state']
	home = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	game_status = MLB_data_json['events'][game_number]['status']['type']['shortDetail']
	try:
		home_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
		visitor_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
		home_record_list = re.split('[-()]', home_record)
		visitor_record_list = re.split('[-()]', visitor_record)
		home_total_games = 0
		visitor_total_games = 0
		for i in home_record_list:
			home_total_games = home_total_games + int(i)
		for i in visitor_record_list:
			visitor_total_games = visitor_total_games + int(i)
	except:
		home_record = ""
		visitor_record = ""	
	try:
		weather = MLB_data_json['events'][game_number]['weather']['displayValue']
		temperature = MLB_data_json['events'][game_number]['weather']['temperature']
	except:
		weather = ""
		temperature = ""
	try:
		broadcast = MLB_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = ""
	try:
		odds = MLB_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
	except:
		odds = ""
	try:
		series = MLB_data_json['events'][game_number]['competitions'][0]['series']['summary']
	except:
		series = ""
	try:
		notes = MLB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes = ""

	home_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['abbreviation']
	visitor_short = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['abbreviation']
	
	try:
		home_probable = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['probables'][0]['athlete']['displayName']
		home_probable_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['probables'][0]['statistics'][2]['displayValue'] + "-" + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['probables'][0]['statistics'][1]['displayValue'] + "-" + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['probables'][0]['statistics'][0]['displayValue'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['probables'][0]['statistics'][3]['displayValue'] + " ERA"
	except:
		home_probable = ""
		home_probable_record = ""
	
	try:
		visitor_probable = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['probables'][0]['athlete']['displayName']
		visitor_probable_record = MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['probables'][0]['statistics'][2]['displayValue'] + "-" + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['probables'][0]['statistics'][1]['displayValue'] + "-" + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['probables'][0]['statistics'][0]['displayValue'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['probables'][0]['statistics'][3]['displayValue'] + " ERA"
	except:
		visitor_probable = ""
		visitor_probable_record = ""

	if home_total_games != 0:
		home_rpg = " (" + str(round(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue']) / home_total_games, 2)) + ")"
		home_hpg = " (" + str(round(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']) / home_total_games, 2)) + ")"
	else:
		home_rpg = ""
		home_hpg = ""

	if visitor_total_games != 0:
		visitor_rpg = " (" + str(round(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue']) / visitor_total_games, 2)) + ")"
		visitor_hpg = " (" + str(round(int(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']) / visitor_total_games, 2)) + ")"
	else:
		visitor_rpg = ""
		visitor_hpg = ""
	
	home_totals = " Team Totals: " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue']) + home_rpg + " Runs, " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']) + home_hpg + " Hits, " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue']) + " Avg., " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']) + " ERA"
	visitor_totals = " Team Totals: " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue']) + visitor_rpg + " Runs, " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']) + visitor_hpg + " Hits, " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue']) + " Avg., " + str(MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']) + " ERA"
	
	home_leaders = " Team Leaders: " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['displayValue'] + " Avg., " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['displayValue'] + " HR, " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['displayValue'] + " RBI"
	visitor_leaders = " Team Leaders: " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['displayValue'] + " Avg., " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['displayValue'] + " HR, " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['fullName'] + " " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['position']['abbreviation'] + ", " + MLB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['displayValue'] + " RBI"

	print(visitor, "("+visitor_record+")", "at", home, "("+home_record+")", "\n", game_status+",", stadium)
	series_status = " "
	if notes != "":
		series_status = series_status + notes + ", "
	if series != "":
		series_status = series_status + series
	else:
		series_status = series_status[:-2]
	if series_status != "":
		print(series_status)
	misc_status = " "
	if weather != "" and temperature != "":
		misc_status = misc_status+weather+", "+str(temperature)+", "
	if broadcast != "":
		misc_status = misc_status+broadcast+", "
	if odds != "":
		misc_status = misc_status+"LINE: "+odds
	if misc_status != " ":
		print(misc_status)
	print()
	print(" " + visitor_short + " Probable Starting Pitcher: " + visitor_probable + " (" + visitor_probable_record + ")")
	print(visitor_totals)
	print(visitor_leaders)
	print()
	print(" " + home_short + " Probable Starting Pitcher: " + home_probable + " (" + home_probable_record + ")")
	print(home_totals)
	print(home_leaders)
	print()
	
#Mainline
#Due to API throttling of requesting more than one day at a time, only 1 day is supported as an optional parameter. Script this program if more than 1 day desired. Due to issues with throttling, wait 1 minute between calls of this program for 1 day of box scores.

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=" + date_arg + "-" + date_arg
	try:
		game_date = datetime.datetime(int(date_arg[0:4]), int(date_arg[4:6]), int(date_arg[6:8]))     
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
	print("----------------------------------------------------------------------")
	print("Games of " + game_date.strftime("%B %-d, %Y"))
else:
	url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

try:
	MLB_today = urlopen(url)
except:
	print("No games on this date.")         #If get past datetime above, date is OK, so API error due to no games.
	exit()

MLB_data_json = json.loads(MLB_today.read())

for game in range(0, 20):
	try: 
		game_state = MLB_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			MLB_post_game(game)
		elif game_state == "in":
			MLB_in_progress(game)
		else:
			MLB_pre_game(game)
	except IndexError:
		continue