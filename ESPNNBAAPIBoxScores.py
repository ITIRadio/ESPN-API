from urllib.request import urlopen
import json
import sys
import datetime
import re
from rich.console import Console
from rich.table import Table

#Summary: mainline code at bottom, call the ESPN NBA Scoreboard API to get current list of games;
#There are 4 possible statuses for each game, post-game, during the game, pre-game, or other, usually a game in postponement,
#for which there will be such a status posted, but otherwise default to pre-game status.
#Then, the game is sent to one of three def's, which will then make another API call for that particular "event", in API terminology.
#At this point, there are two active Python dictionaries converted from the JSON data retunred from the API calls:
#1. NBA_data_json, the global dictionary for all games, from which a few stats are pulled,
#2. NBA_event_data_json, the detailed stats for that particular game being readied for display.
#Within each def, appropriate stats are pulled from the appropriate dictionary, and Python strings are built for display.
#Because Python/Linux display options are far too limited, the Raspberry Pi ticker idea was abandoned,
#so these stats are dumped to the terminal for viewing or redirection.
#Usage: python3 -u ESPNNBAAPIBoxScores.py YYYYMMDD
#Date parameter optional, add 2nd date in same format for a date range, otherwise get games on current scoreboard
#IMPORTANT:
#The rich text library must be installed, run the command "pip install rich" if necessary. 

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def NBA_post_game(game_number):

	event_id = NBA_data_json['events'][game_number]['id']
	event_url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event=" + event_id
	NBA_event = urlopen(event_url)
	NBA_event_data_json = json.loads(NBA_event.read())
	
	console = Console()
	
	home = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	home_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
	home_player_stats = Table(box=None, header_style="default")
	home_player_stats.add_column(home_short + " (" + home_record + ")")
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
	
	for player in range(0, 20):
		try:
			try:
				player_name = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_min = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0]                 
			player_fg = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1]
			player_3pt = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][2]
			player_ft = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3]
			player_reb = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][6]
			player_oreb = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4]                
			player_ast = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][7]
			player_stl = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][8]                 
			player_blk = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][9]                 
			player_to = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][10]                
			player_fl = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][11]
			player_pts = NBA_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][13]
			home_player_stats.add_row(player_name, player_min, player_fg, player_3pt, player_ft, player_reb, player_oreb, player_ast, player_to, player_stl, player_blk, player_fl, player_pts)
		except IndexError:
			continue

	home_score = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']
	home_off_reb = NBA_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue']
	home_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue']
	home_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
	home_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
	home_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][15]['displayValue']
	home_3pt_made = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][12]['displayValue']
	home_3pt_att = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][11]['displayValue']
	home_fgm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue']
	home_fga = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][3]['displayValue']
	home_ftm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue']
	home_fta = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][7]['displayValue']
	home_to = NBA_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue']
	home_stl = NBA_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue']
	home_blk = NBA_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue']
	home_fls = NBA_event_data_json['boxscore']['teams'][1]['statistics'][21]['displayValue']

	home_player_stats.add_row("Totals", "", home_fgm + "-" + home_fga, home_3pt_made + "-" + home_3pt_att, home_ftm + "-" + home_fta, home_rebounds, home_off_reb, home_assists, home_to, home_stl, home_blk, home_fls, home_score)
	home_player_stats.add_row("", "", home_fg_pct + "%", home_3pt_pct + "%", home_ft_pct + "%", "", "", "", "", "", "", "", "")
	
	home_qtrs = ""	
	for qtr in range(0, 12):
		try:
			home_qtrs = home_qtrs + str(int(NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if home_qtrs != "":                         #Remove extra + at end
		home_qtrs = home_qtrs[:-3]
	
	home_extra_stats = " Score by Quarters: " + home_qtrs + "\n " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][15]['displayValue']) + " Technicals, " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][17]['displayValue']) + " Flagrant Fouls, " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][22]['displayValue']) + " Largest Lead, " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][18]['displayValue']) + " Points off Turnovers, " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][19]['displayValue']) + " Fast Break Points, " + str(NBA_event_data_json['boxscore']['teams'][1]['statistics'][20]['displayValue']) + " Points in the Paint"
	
	visitor = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	visitor_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	visitor_player_stats = Table(box=None, header_style="default")
	visitor_player_stats.add_column(visitor_short + " (" + visitor_record + ")")
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
	
	for player in range(0, 20):
		try:
			try:
				player_name = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName']
			except:
				player_name = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['shortName']
			player_min = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0]                
			player_fg = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1]
			player_3pt = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][2]
			player_ft = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3]
			player_reb = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][6]
			player_oreb = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4]               
			player_ast = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][7]
			player_stl = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][8]                
			player_blk = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][9]                 
			player_to = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][10]                
			player_fl = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][11]
			player_pts = NBA_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][13]
			visitor_player_stats.add_row(player_name, player_min, player_fg, player_3pt, player_ft, player_reb, player_oreb, player_ast, player_to, player_stl, player_blk, player_fl, player_pts)
		except IndexError:
			continue

	visitor_score = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	visitor_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']
	visitor_off_reb = NBA_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue']
	visitor_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue']
	visitor_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
	visitor_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
	visitor_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][15]['displayValue']
	visitor_3pt_made = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][12]['displayValue']
	visitor_3pt_att = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][11]['displayValue']
	visitor_fgm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue']
	visitor_fga = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][3]['displayValue']
	visitor_ftm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue']
	visitor_fta = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][7]['displayValue']
	visitor_to = NBA_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue']
	visitor_stl = NBA_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue']
	visitor_blk = NBA_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue']
	visitor_fls = NBA_event_data_json['boxscore']['teams'][0]['statistics'][21]['displayValue']

	visitor_player_stats.add_row("Totals", "", visitor_fgm + "-" + visitor_fga, visitor_3pt_made + "-" + visitor_3pt_att, visitor_ftm + "-" + visitor_fta, visitor_rebounds, visitor_off_reb, visitor_assists, visitor_to, visitor_stl, visitor_blk, visitor_fls, visitor_score)
	visitor_player_stats.add_row("", "", visitor_fg_pct + "%", visitor_3pt_pct + "%", visitor_ft_pct + "%", "", "", "", "", "", "", "", "")
	
	visitor_qtrs = ""
	for qtr in range(0, 12):
		try:
			visitor_qtrs = visitor_qtrs + str(int(NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if visitor_qtrs != "":
		visitor_qtrs = visitor_qtrs[:-3]
	
	visitor_extra_stats = " Score by Quarters: " + visitor_qtrs + "\n " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][15]['displayValue']) + " Technicals, " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][17]['displayValue']) + " Flagrant Fouls, " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][22]['displayValue']) + " Largest Lead, " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][18]['displayValue']) + " Points off Turnovers, " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][19]['displayValue']) + " Fast Break Points, " + str(NBA_event_data_json['boxscore']['teams'][0]['statistics'][20]['displayValue']) + " Points in the Paint"

	arena = NBA_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	game_status = NBA_data_json['events'][game_number]['status']['type']['detail']
	try:
		headline = NBA_data_json['events'][game_number]['competitions'][0]['headlines'][0]['shortLinkText']
	except:
		headline = ""
	try:                           
		notes = NBA_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NBA_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass
	
	try:
		article = NBA_event_data_json['article']['story']
	except:
		article = ""
	if article != "":
		article = re.sub(r'<.*?>', '', article)
		article = re.sub(' +', ' ', article)
		article = re.sub('\r', '', article)
		article = re.sub('\n\n\n ', '\n', article)

	visitor_len = len(visitor + " " + str(visitor_score))
	home_len = len(home + " " + str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
		
	print(visitor, "  " + visitor_add_spc, visitor_score)
	print(home, "  " + home_add_spc, home_score, game_status, arena)
	if notes != "":
		print(notes)
	if headline != "":
		print(headline + "\n")
	else:                          
		print()

	console.print(visitor_player_stats)
	print()
	print(visitor_extra_stats)
	print()
	console.print(home_player_stats)
	print()
	print(home_extra_stats)

	if article != "":
		print()
		print(article)
	print()
	
def NBA_in_progress(game_number):

	arena = NBA_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_score = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score']
	home_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][0]['displayValue']
	home_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][2]['displayValue']
	home_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
	home_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
	home_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][15]['displayValue']
	home_3pt_made = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][12]['displayValue']
	home_3pt_att = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][11]['displayValue']
	home_fgm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][4]['displayValue']
	home_fga = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][3]['displayValue']
	home_ftm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][8]['displayValue']
	home_fta = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][7]['displayValue']
	try:
		home_leader_0 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['shortDisplayName']
		home_leader_0_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['displayValue']
		home_leader_0_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['displayName']
		home_leader_1 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['shortDisplayName']
		home_leader_1_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['displayValue']
		home_leader_1_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['displayName']
		home_leader_2 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['shortDisplayName']
		home_leader_2_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['displayValue']
		home_leader_2_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['displayName']
		home_leader_status = " "
	except:
		home_leader_status = ""
	home_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	visitor = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_score = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score']
	try:
		visitor_leader_0 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['shortDisplayName']
		visitor_leader_0_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['displayValue']
		visitor_leader_0_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['displayName']
		visitor_leader_1 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['shortDisplayName']
		visitor_leader_1_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['displayValue']
		visitor_leader_1_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['displayName']
		visitor_leader_2 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['shortDisplayName']
		visitor_leader_2_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['displayValue']
		visitor_leader_2_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['displayName']
		visitor_leader_status = " "
	except:
		visitor_leader_status = ""
	visitor_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][0]['displayValue']
	visitor_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][2]['displayValue']
	visitor_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
	visitor_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
	visitor_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][15]['displayValue']
	visitor_3pt_made = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][12]['displayValue']
	visitor_3pt_att = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][11]['displayValue']
	visitor_fgm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][4]['displayValue']
	visitor_fga = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][3]['displayValue']
	visitor_ftm = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][8]['displayValue']
	visitor_fta = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][7]['displayValue']
	visitor_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	game_status = NBA_data_json['events'][game_number]['status']['type']['detail']
	home_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
	visitor_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	try:
		broadcast = NBA_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	try:
		notes = NBA_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NBA_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass
	visitor_len = len(visitor+" ("+visitor_record+") "+visitor_score)
	home_len = len(home+" ("+home_record+") "+home_score)
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	print(visitor, "("+visitor_record+")  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+")  "+home_add_spc, home_score)
	print(game_status+",", arena+",", broadcast)
	if notes != "":
		print(notes)
	print(" "+visitor_short+":", str(visitor_fgm)+"/"+str(visitor_fga), visitor_fg_pct, "FG%,", str(visitor_3pt_made)+"/"+str(visitor_3pt_att), visitor_3pt_pct, "3PT%,", str(visitor_ftm)+"/"+str(visitor_fta), visitor_ft_pct, "FT%,", visitor_rebounds, "Reb,", visitor_assists, "Ast")
	if visitor_leader_status != "":
		print(" "+visitor_leader_0_player, visitor_leader_0_stat, visitor_leader_0+",", visitor_leader_1_player, visitor_leader_1_stat, visitor_leader_1+",", visitor_leader_2_player, visitor_leader_2_stat, visitor_leader_2)
	else:
		print()
	print(" "+home_short+":", str(home_fgm)+"/"+str(home_fga), home_fg_pct, "FG%,", str(home_3pt_made)+"/"+str(home_3pt_att), home_3pt_pct, "3PT%,", str(home_ftm)+"/"+str(home_fta), home_ft_pct, "FT%,", home_rebounds, "Reb,", home_assists, "Ast")
	if home_leader_status != "":
		print(" "+home_leader_0_player, home_leader_0_stat, home_leader_0+",", home_leader_1_player, home_leader_1_stat, home_leader_1+",", home_leader_2_player, home_leader_2_stat, home_leader_2, "\n")
	else:
		print()

def NBA_pre_game(game_number):

	arena = NBA_data_json['events'][game_number]['competitions'][0]['venue']['fullName']
	home = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['displayName']
	home_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][1]['displayValue']
	home_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][14]['displayValue']
	home_points = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][13]['displayValue']
	home_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][5]['displayValue']
	home_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][6]['displayValue']
	home_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['statistics'][15]['displayValue']
	home_leader_0 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['shortDisplayName']
	home_leader_0_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['displayValue']
	home_leader_0_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][0]['leaders'][0]['athlete']['displayName']
	home_leader_1 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['shortDisplayName']
	home_leader_1_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['displayValue']
	home_leader_1_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][1]['leaders'][0]['athlete']['displayName']
	home_leader_2 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['shortDisplayName']
	home_leader_2_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['displayValue']
	home_leader_2_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['leaders'][2]['leaders'][0]['athlete']['displayName']
	home_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['records'][0]['summary']
	visitor = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['displayName']
	visitor_leader_0 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['shortDisplayName']
	visitor_leader_0_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['displayValue']
	visitor_leader_0_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][0]['leaders'][0]['athlete']['displayName']
	visitor_leader_1 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['shortDisplayName']
	visitor_leader_1_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['displayValue']
	visitor_leader_1_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][1]['leaders'][0]['athlete']['displayName']
	visitor_leader_2 = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['shortDisplayName']
	visitor_leader_2_stat = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['displayValue']
	visitor_leader_2_player = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['leaders'][2]['leaders'][0]['athlete']['displayName']
	visitor_rebounds = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][1]['displayValue']
	visitor_assists = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][14]['displayValue']
	visitor_points = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][13]['displayValue']
	visitor_fg_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][5]['displayValue']
	visitor_ft_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][6]['displayValue']
	visitor_3pt_pct = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['statistics'][15]['displayValue']
	visitor_record = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['records'][0]['summary']
	game_status = NBA_data_json['events'][game_number]['status']['type']['detail']
	home_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][0]['team']['shortDisplayName']
	visitor_short = NBA_data_json['events'][game_number]['competitions'][0]['competitors'][1]['team']['shortDisplayName']
	try:
		broadcast = NBA_data_json['events'][game_number]['competitions'][0]['broadcasts'][0]['names'][0]
	except:
		broadcast = "No Nat'l TV"
	try:
		odds = NBA_data_json['events'][game_number]['competitions'][0]['odds'][0]['details']
	except:
		odds=""
	try:
		notes = NBA_data_json['events'][game_number]['competitions'][0]['notes'][0]['headline']
	except:
		notes=""
	try:
		series = NBA_data_json['events'][game_number]['competitions'][0]['series']['summary']
		notes = notes + ", " + series
	except:
		pass
	print(visitor, "("+visitor_record+")", "at", home, "("+home_record+")", "\n", visitor_short+":", visitor_fg_pct, "FG%,", visitor_3pt_pct, "3PT%,", visitor_ft_pct, "FT%,", visitor_points, "PPG,", visitor_rebounds, "RPG,", visitor_assists, "APG,", "\n", visitor_leader_0_player, visitor_leader_0_stat, visitor_leader_0+",", visitor_leader_1_player, visitor_leader_1_stat, visitor_leader_1+",", visitor_leader_2_player, visitor_leader_2_stat, visitor_leader_2, "\n", home_short+":", home_fg_pct, "FG%,", home_3pt_pct, "3PT%,", home_ft_pct, "FT%,", home_points, "PPG,", home_rebounds, "RPG,", home_assists, "APG,", "\n", home_leader_0_player, home_leader_0_stat, home_leader_0+",", home_leader_1_player, home_leader_1_stat, home_leader_1+",", home_leader_2_player, home_leader_2_stat, home_leader_2, "\n", game_status+",", arena+",", broadcast)
	if notes != "":
		print(" " + notes)
	print(" LINE:", odds, "\n")

#Mainline

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=" + date_arg + "-" + date_arg
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
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=" + date1_arg + "-" + date2_arg
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
	url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

try:
	NBA_today = urlopen(url)
except:
	print("No games on this date, or use earlier date first if entering two dates.")
	exit()

NBA_data_json = json.loads(NBA_today.read())

for game in range(0, 25):
	try:
		game_state = NBA_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			NBA_post_game(game)
		elif game_state == "in":
			NBA_in_progress(game)
		else:
			NBA_pre_game(game)
	except IndexError:
		continue
