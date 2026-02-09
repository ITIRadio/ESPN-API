from urllib.request import urlopen
import json
import sys
from datetime import datetime       #Necessary for date conversion
import pytz                         #Dates are in UTC, though never specified
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN CBB Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. CBB_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. CBB_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Usage: python3 ESPNCBBAPIBoxScores.py YYYYMMDD
#Date parameter optional, add 2nd date in same format for a date range, otherwise get games on current scoreboard
#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def CBB_post_game(game_number):

	event_id = CBB_data_json['events'][game_number]['id']
	event_url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event=" + event_id
	CBB_event = urlopen(event_url)
	CBB_event_data_json = json.loads(CBB_event.read())
	
	console = Console()
	
	#Regular data from scoreboard API, leave leaders assignments for future use
	try:
		arena = CBB_data_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + CBB_data_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + CBB_data_json['events'][game_number]['competitions'][0]['venue']['address']['state']
	except:
		arena = ""
	home = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	visitor = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	game_status = CBB_data_json['events'][game_number]['status']['type']['detail']
	json_tz = pytz.timezone("UTC")
	needed_tz = pytz.timezone("US/Eastern")
	game_date = datetime.strptime(CBB_data_json['events'][game_number]['competitions'][0]['date'], "%Y-%m-%dT%H:%MZ") #Convert whole json date to datetime obj, but in UTC timezone, skip use on other api's
	game_date = json_tz.localize(game_date).astimezone(needed_tz)       #Convert game_date datetime obj from UTC to US Eastern
	game_date = game_date.strftime("%m-%d-%Y")    #Convert datetime obj to mm-dd-yyyy
	#Blank record OK, but some short names don't exist
	try:
		home_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
		visitor_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	except:
		home_short = home
		visitor_short = visitor
	try:
		visitor_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		visitor_record = ""
	try:
		home_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	except:
		home_record = ""
	try:
		visitor_conf_record = ", " + CBB_event_data_json['header']['competitions'][0]['competitors'][1]['record'][2]['displayValue']
	except:
		visitor_conf_record = ""
	try:
		home_conf_record = ", " + CBB_event_data_json['header']['competitions'][0]['competitors'][0]['record'][2]['displayValue']
	except:
		home_conf_record = ""
	try:
		notes = CBB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		home_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
		visitor_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		home_rank = 99
		visitor_rank = 99
	try:
		headline = CBB_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	
	home_player_stats = Table(box=None, header_style="default")
	home_player_stats.add_column(home_short)
	home_player_stats.add_column("Pos")
	home_player_stats.add_column("Min", justify="right")
	home_player_stats.add_column("FG", justify="right")
	home_player_stats.add_column("3-pt", justify="right")
	home_player_stats.add_column("FT", justify="right")
	home_player_stats.add_column("Tot Reb", justify="right")
	home_player_stats.add_column("Off Reb", justify="right")
	home_player_stats.add_column("Ast", justify="right")
	home_player_stats.add_column("TO", justify="right")
	home_player_stats.add_column("Stl", justify="right")
	home_player_stats.add_column("Blk", justify="right")
	home_player_stats.add_column("Fls", justify="right")
	home_player_stats.add_column("Pts", justify="right")
	
	home_rebounds = 0
	home_off_reb = 0
	
	for player in range(0, 25):
		try:
			try:
				player_name = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_name_short = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['shortName']
			try:
				player_nbr = str(CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['jersey'])
				player_name = player_name + " (" + player_nbr + ")"
			except:
				pass
			try:
				player_pos = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['position']['abbreviation']
				if player_pos == "ATH":
					player_pos = ""
				if int(CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['starter']) == 1:
					player_pos = player_pos + "*"
			except:
				player_pos = ""
			player_min = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0]
			player_fg = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][2]
			player_3pt = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3]
			player_ft = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4]
			player_reb = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][5]
			player_oreb = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][10]
			player_ast = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][6]
			player_stl = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][8]
			player_blk = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][9]
			player_to = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][7]
			player_fl = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][12]
			player_pts = CBB_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1]
			home_rebounds += int(player_reb)
			home_off_reb += int(player_oreb)
			home_player_stats.add_row(player_name, player_pos, player_min, player_fg, player_3pt, player_ft, player_reb, player_oreb, player_ast, player_to, player_stl, player_blk, player_fl, player_pts)
			
		except (IndexError, KeyError, ValueError) as api_bad_data_problem:
			continue
	
	home_score = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_ttl_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']
#	home_off_reb = CBB_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue']  Not using this, using own ttl, w/o tm rebs
	home_team_rebs = int(home_ttl_rebounds) - home_rebounds
	home_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue']
	home_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
	home_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
	home_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][14]['displayValue']
	home_3pt_made = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][11]['displayValue']
	home_3pt_att = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][10]['displayValue']
	home_fgm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue']
	home_fga = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][3]['displayValue']
	home_ftm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue']
	home_fta = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][7]['displayValue']
	home_to = CBB_event_data_json['boxscore']['teams'][1]['statistics'][12]['displayValue']
	home_stl = CBB_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue']
	home_blk = CBB_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue']
	home_fls = CBB_event_data_json['boxscore']['teams'][1]['statistics'][21]['displayValue']
	
	home_player_stats.add_row("Team Rebounds", "", "", "", "", "", str(home_team_rebs), "", "", "", "", "", "", "", "")
	home_player_stats.add_row("Totals", "", "", home_fgm + "-" + home_fga, home_3pt_made + "-" + home_3pt_att, home_ftm + "-" + home_fta, home_ttl_rebounds, str(home_off_reb), home_assists, home_to, home_stl, home_blk, home_fls, home_score)
	home_player_stats.add_row("", "", "", home_fg_pct + "%", home_3pt_pct + "%", home_ft_pct + "%", "", "", "", "", "", "", "", "")
	
	visitor_player_stats = Table(box=None, header_style="default")
	visitor_player_stats.add_column(visitor_short)
	visitor_player_stats.add_column("Pos")
	visitor_player_stats.add_column("Min", justify="right")
	visitor_player_stats.add_column("FG", justify="right")
	visitor_player_stats.add_column("3-pt", justify="right")
	visitor_player_stats.add_column("FT", justify="right")
	visitor_player_stats.add_column("Tot Reb", justify="right")
	visitor_player_stats.add_column("Off Reb", justify="right")
	visitor_player_stats.add_column("Ast", justify="right")
	visitor_player_stats.add_column("TO", justify="right")
	visitor_player_stats.add_column("Stl", justify="right")
	visitor_player_stats.add_column("Blk", justify="right")
	visitor_player_stats.add_column("Fls", justify="right")
	visitor_player_stats.add_column("Pts", justify="right")
	
	visitor_rebounds = 0
	visitor_off_reb = 0
	
	for player in range(0, 25):
		try:
			try:
				player_name = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_name_short = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['shortName']
			try:
				player_nbr = str(CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['jersey'])
				player_name = player_name + " (" + player_nbr + ")"
			except:
				pass
			try:
				player_pos = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['position']['abbreviation']
				if player_pos == "ATH":
					player_pos = ""
				if int(CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['starter']) == 1:
					player_pos = player_pos + "*"
			except:
				player_pos = ""
			player_min = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0]
			player_fg = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][2]
			player_3pt = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3]
			player_ft = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4]
			player_reb = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][5]
			player_oreb = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][10]
			player_ast = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][6]
			player_stl = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][8]
			player_blk = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][9]
			player_to = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][7]
			player_fl = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][12]
			player_pts = CBB_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1]
			visitor_rebounds += int(player_reb)
			visitor_off_reb += int(player_oreb)
			visitor_player_stats.add_row(player_name, player_pos, player_min, player_fg, player_3pt, player_ft, player_reb, player_oreb, player_ast, player_to, player_stl, player_blk, player_fl, player_pts)
			
		except (IndexError, KeyError, ValueError) as api_bad_data_problem:
			continue
	
	visitor_score = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_ttl_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']
#	visitor_off_reb = CBB_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue']
	visitor_team_rebs = int(visitor_ttl_rebounds) - visitor_rebounds
	visitor_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue']
	visitor_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
	visitor_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
	visitor_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][14]['displayValue']
	visitor_3pt_made = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][11]['displayValue']
	visitor_3pt_att = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][10]['displayValue']
	visitor_fgm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue']
	visitor_fga = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][3]['displayValue']
	visitor_ftm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue']
	visitor_fta = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][7]['displayValue']
	visitor_to = CBB_event_data_json['boxscore']['teams'][0]['statistics'][12]['displayValue']
	visitor_stl = CBB_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue']
	visitor_blk = CBB_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue']
	visitor_fls = CBB_event_data_json['boxscore']['teams'][0]['statistics'][21]['displayValue']
	
	visitor_player_stats.add_row("Team Rebounds", "", "", "", "", "", str(visitor_team_rebs), "", "", "", "", "", "", "", "")
	visitor_player_stats.add_row("Totals", "", "", visitor_fgm + "-" + visitor_fga, visitor_3pt_made + "-" + visitor_3pt_att, visitor_ftm + "-" + visitor_fta, visitor_ttl_rebounds, str(visitor_off_reb), visitor_assists, visitor_to, visitor_stl, visitor_blk, visitor_fls, visitor_score)
	visitor_player_stats.add_row("", "", "", visitor_fg_pct + "%", visitor_3pt_pct + "%", visitor_ft_pct + "%", "", "", "", "", "", "", "", "")
	
	team_comparison = Table(box=None, header_style="default")
	team_comparison.add_column("Team Comparison")
	team_comparison.add_column(str(CBB_event_data_json['header']['competitions'][0]['competitors'][1]['team']['abbreviation']))
	team_comparison.add_column(str(CBB_event_data_json['header']['competitions'][0]['competitors'][0]['team']['abbreviation']))
	team_comparison.add_row("Halftime Score", str(int(CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][0]['value'])), str(int(CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][0]['value'])))
	team_comparison.add_row("Largest Lead", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][22]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][22]['displayValue']))
	team_comparison.add_row("Points in the Paint", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][20]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][20]['displayValue']))
	team_comparison.add_row("Fast Break Points", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][19]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][19]['displayValue']))
	team_comparison.add_row("Points off Turnovers", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][18]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][18]['displayValue']))
	team_comparison.add_row("Technical Fouls", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][16]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][16]['displayValue']))
	team_comparison.add_row("Flagrant Fouls", str(CBB_event_data_json['boxscore']['teams'][0]['statistics'][17]['displayValue']), str(CBB_event_data_json['boxscore']['teams'][1]['statistics'][17]['displayValue']))
	
	try:
		article = CBB_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)
	
	if home_rank == 99:
		home_rank = ""
	else:
		home_rank = ", #"+str(home_rank)
	if visitor_rank == 99:
		visitor_rank = ""
	else:
		visitor_rank = ", #"+str(visitor_rank)
	visitor_len = len(visitor+" ("+visitor_record+visitor_conf_record+visitor_rank+") "+visitor_score)
	home_len = len(home+" ("+home_record+home_conf_record+home_rank+") "+home_score)
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	print()
	print(visitor, "("+visitor_record+visitor_conf_record+visitor_rank+")  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+home_conf_record+home_rank+")  "+home_add_spc, home_score, game_status, arena + ", " + game_date)
	if notes != "":
		print(notes)
	if headline != "":
		print(headline)
	print()
	console.print(visitor_player_stats)
	print()
	console.print(home_player_stats)
	print()
	console.print(team_comparison)
	
	if article != "":
		print()
		print(article)
	print()
	print("----------------------------------------")

def CBB_in_progress(game_number):

	arena = CBB_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']
	home_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue']
	home_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
	home_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
	home_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][14]['displayValue']
	home_3pt_made = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][11]['displayValue']
	home_3pt_att = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][10]['displayValue']
	home_fgm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue']
	home_fga = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][3]['displayValue']
	home_ftm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue']
	home_fta = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][7]['displayValue']
	try:
		home_leader_0 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['shortDisplayName']
		home_leader_0_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['displayValue']
		home_leader_0_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['displayName']
		home_leader_1 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['shortDisplayName']
		home_leader_1_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['displayValue']
		home_leader_1_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['displayName']
		home_leader_2 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['shortDisplayName']
		home_leader_2_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['displayValue']
		home_leader_2_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['displayName']
		home_leader_status = " "
	except:
		home_leader_status = ""
	visitor = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	try:
		visitor_leader_0 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['shortDisplayName']
		visitor_leader_0_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['displayValue']
		visitor_leader_0_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['displayName']
		visitor_leader_1 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['shortDisplayName']
		visitor_leader_1_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['displayValue']
		visitor_leader_1_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['displayName']
		visitor_leader_2 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['shortDisplayName']
		visitor_leader_2_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['displayValue']
		visitor_leader_2_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['displayName']
		visitor_leader_status = " "
	except:
		visitor_leader_status = ""
	visitor_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']
	visitor_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue']
	visitor_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
	visitor_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
	visitor_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][14]['displayValue']
	visitor_3pt_made = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][11]['displayValue']
	visitor_3pt_att = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][10]['displayValue']
	visitor_fgm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue']
	visitor_fga = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][3]['displayValue']
	visitor_ftm = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue']
	visitor_fta = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][7]['displayValue']
	game_status = CBB_data_json['events'][game_number]['status']['type']['detail']
	try:
		home_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
		visitor_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	except:
		home_short = home
		visitor_short = visitor
	try:
		visitor_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		visitor_record = ""
	try:
		home_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	except:
		home_record = ""
	try:
		home_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
		visitor_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		home_rank = 99
		visitor_rank = 99
	try:                                     #Not all broadcast, stops whole game if blank, watch other games, chg to no nat'l tv
		broadcast = CBB_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	try:
		notes = CBB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	if home_rank == 99:
		home_rank = ""
	else:
		home_rank = ", #"+str(home_rank)
	if visitor_rank == 99:
		visitor_rank = ""
	else:
		visitor_rank = ", #"+str(visitor_rank)
	visitor_len = len(visitor+" ("+visitor_record+visitor_rank+") "+visitor_score)
	home_len = len(home+" ("+home_record+home_rank+") "+home_score)
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)

	print(visitor, "("+visitor_record+visitor_rank+")  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+home_rank+")  "+home_add_spc, home_score)
	print(game_status+",", broadcast)
	if notes != "":
		print(" "+notes)
	print(" "+visitor_short+":", str(visitor_fgm)+"/"+str(visitor_fga), visitor_fg_pct, "FG%,", str(visitor_3pt_made)+"/"+str(visitor_3pt_att), visitor_3pt_pct, "3PT%,", str(visitor_ftm)+"/"+str(visitor_fta), visitor_ft_pct, "FT%,", visitor_rebounds, "Reb,", visitor_assists, "Ast")
	if visitor_leader_status == " ":
		print(" "+visitor_leader_0_player, visitor_leader_0_stat, visitor_leader_0+",", visitor_leader_1_player, visitor_leader_1_stat, visitor_leader_1+",", visitor_leader_2_player, visitor_leader_2_stat, visitor_leader_2)
	print(" "+home_short+":", str(home_fgm)+"/"+str(home_fga), home_fg_pct, "FG%,", str(home_3pt_made)+"/"+str(home_3pt_att), home_3pt_pct, "3PT%,", str(home_ftm)+"/"+str(home_fta), home_ft_pct, "FT%,", home_rebounds, "Reb,", home_assists, "Ast")
	if home_leader_status == " ":
		print(" "+home_leader_0_player, home_leader_0_stat, home_leader_0+",", home_leader_1_player, home_leader_1_stat, home_leader_1+",", home_leader_2_player, home_leader_2_stat, home_leader_2, "\n")
	else:
		print()

def CBB_pre_game(game_number):
	
	home = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	try:
		home_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue']
		home_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][13]['displayValue']
		home_points = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][12]['displayValue']
		home_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
		home_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
		home_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][14]['displayValue']
		home_blank = " "
	except:
		home_blank = ""
	
	#Visiting team info & data
	visitor = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	try:
		visitor_rebounds = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue']
		visitor_assists = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][13]['displayValue']
		visitor_points = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][12]['displayValue']
		visitor_fg_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
		visitor_ft_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
		visitor_3pt_pct = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][14]['displayValue']
		visitor_blank = " "
	except:
		visitor_blank = ""
	
	try:  #If any stat leaders are missing, just skip those stat lines
		home_leader_0 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['shortDisplayName']
		home_leader_0_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['displayValue']
		home_leader_0_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['displayName']
		home_leader_1 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['shortDisplayName']
		home_leader_1_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['displayValue']
		home_leader_1_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['displayName']
		home_leader_2 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['shortDisplayName']
		home_leader_2_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['displayValue']
		home_leader_2_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['displayName']
		visitor_leader_0 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['shortDisplayName']
		visitor_leader_0_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['displayValue']
		visitor_leader_0_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['displayName']
		visitor_leader_1 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['shortDisplayName']
		visitor_leader_1_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['displayValue']
		visitor_leader_1_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['displayName']
		visitor_leader_2 = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['shortDisplayName']
		visitor_leader_2_stat = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['displayValue']
		visitor_leader_2_player = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['displayName']
		leaders_blank = " "
	except:
		leaders_blank = ""

	try:   #Gather ranks if top 25 team; if not, rank, if available, is 99
		home_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['curatedRank']['current']
		visitor_rank = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['curatedRank']['current']
	except:
		home_rank = 99
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
		home_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
		visitor_short = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	except:
		home_short = home
		visitor_short = visitor
	try:
		visitor_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	except:
		visitor_record = ""
	try:
		home_record = CBB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	except:
		home_record = ""

	try:   #Gather broadcaster, odds, & notes (such as tournament & round) as available
		broadcast = CBB_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	try:
		odds = CBB_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
	except:
		odds=""
	try:
		notes = CBB_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""

	try:
		arena = CBB_data_json['events'][game_number]['competitions'][0]['venue']['fullName'] + ", " + CBB_data_json['events'][game_number]['competitions'][0]['venue']['address']['city'] + ", " + CBB_data_json['events'][game_number]['competitions'][0]['venue']['address']['state']
	except:
		arena = ""

	game_status = CBB_data_json['events'][game_number]['status']['type']['detail']

	print(visitor, "("+visitor_record+visitor_rank+")", "at", home, "("+home_record+home_rank+")")
	if visitor_blank != "":
		print(" "+visitor_short+":", visitor_fg_pct, "FG%,", visitor_3pt_pct, "3PT%,", visitor_ft_pct, "FT%,", visitor_points, "PPG,", visitor_rebounds, "RPG,", visitor_assists, "APG")
	if leaders_blank == " ":
		print(" "+visitor_leader_0_player, visitor_leader_0_stat, visitor_leader_0+",", visitor_leader_1_player, visitor_leader_1_stat, visitor_leader_1+",", visitor_leader_2_player, visitor_leader_2_stat, visitor_leader_2)
	if home_blank != "":
		print(" "+home_short+":", home_fg_pct, "FG%,", home_3pt_pct, "3PT%,", home_ft_pct, "FT%,", home_points, "PPG,", home_rebounds, "RPG,", home_assists, "APG")
	if leaders_blank == " ":
		print(" "+home_leader_0_player, home_leader_0_stat, home_leader_0+",", home_leader_1_player, home_leader_1_stat, home_leader_1+",", home_leader_2_player, home_leader_2_stat, home_leader_2)
	print(" "+game_status+"\n", arena+",", broadcast+", Line:", odds)
	if notes != "":
		print(" "+notes+"\n")
	else:
		print()

#Main procedure

if len(sys.argv) == 2:
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50&limit=200&dates=" + str(sys.argv[1]) + "-" + str(sys.argv[1])
elif len(sys.argv) == 3:
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50&limit=300&dates=" + str(sys.argv[1]) + "-" + str(sys.argv[2])
else:
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50&limit=200"

try:
	CBB_today = urlopen(url)
except:
	print("Incorrect date format, use YYYYMMDD or YYYYMMDD-YYYYMMDD, earlier date first.")
	exit()

CBB_data_json = json.loads(CBB_today.read())

#Iterate through each game, send to the proper def based on game state, drop out of loop once out of games; game & game_number parm is event index
for game in range(0, 200):
	try: 
		game_state = CBB_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			progress_message = "Downloading " + CBB_data_json['events'][game]['competitions'][0]['competitors'][1]['team']['displayName'] + " at " + CBB_data_json['events'][game]['competitions'][0]['competitors'][0]['team']['displayName']
			print(progress_message, file=sys.stderr, flush=True)
			CBB_post_game(game)
		elif game_state == "in":
			CBB_in_progress(game)
		else:
			CBB_pre_game(game)
	except IndexError:
		continue
