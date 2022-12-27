from urllib.request import urlopen
import json

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
#Most Linux distros have json & urllib libraries installed by default; if using another OS, double check.
#Usage: python3 ESPNCFBAPIBoxScores.py

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def CFB_post_game(game_number):
	
	#Make event API call & transfer to dictionary. Note that the game number, or id, is passed into the def for the API call
	#In this API, visiting teams are listed 1st, not 2nd, as in the scoreboard API, then build, in order:
	#Home team box score stats, visiting team box score stats, home & visiting team passing, rushing, & receiving player stats
	#For range loops build players until it runs out of players, and for loop is continued out of
	#There are far too many null data in this REST API, so try/except blocks are necessary & default to blanks as necessary
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())
	
	try:
		home_team_stats = " " + CFB_event_data_json['boxscore']['teams'][1]['team']['abbreviation'] + ": " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][0]['label'] + ", " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'] + " Rushing, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue'] + ", " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue'] + " Yds Passing, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][3]['displayValue'] + " Total Yds, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'] + " Int, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][12]['displayValue'] + " Fum Lost, " + "\n " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][1]['displayValue'] + " 3rd Downs, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][2]['displayValue'] + " 4th Downs, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'] + " Penalties, " + CFB_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue'] + " Possession"
		visitor_team_stats = " " + CFB_event_data_json['boxscore']['teams'][0]['team']['abbreviation'] + ": " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'] + " " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][0]['label'] + ", " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][8]['displayValue'] + "-" + CFB_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'] + " Rushing, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue'] + ", " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue'] + " Yds Passing, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][3]['displayValue'] + " Total Yds, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'] + " Int, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][12]['displayValue'] + " Fum Lost, " + "\n " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][1]['displayValue'] + " 3rd Downs, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][2]['displayValue'] + " 4th Downs, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'] + " Penalties, " + CFB_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue'] + " Possession"
	except:
		home_team_stats = ""
		visitor_team_stats = ""

	#Build all player stats
	
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

	#Build scores by quarters, with OT as necessary

	home_qtrs = ""
	visitor_qtrs = ""
	
	for qtr in range(0, 12):
		try:
			home_qtrs = home_qtrs + str(int(CFB_data_json['events'][game_number]['competitions'][0]['competitors'][0]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if home_qtrs != "":                         #Remove extra + at end
		home_qtrs = home_qtrs[:-3]
		
	for qtr in range(0, 12):
		try:
			visitor_qtrs = visitor_qtrs + str(int(CFB_data_json['events'][game_number]['competitions'][0]['competitors'][1]['linescores'][qtr]['value'])) + " + "
		except IndexError:
			continue
	if visitor_qtrs != "":
		visitor_qtrs = visitor_qtrs[:-3]
		
	#Build scoring play list
	
	scoring_plays = " Scoring Plays:" + "\n "
	for play in range(0,20):
		try:
			scoring_plays = scoring_plays + CFB_event_data_json['scoringPlays'][play]['team']['abbreviation'] + ": " + CFB_event_data_json['scoringPlays'][play]['text'].rstrip().lstrip() + ", Qtr " + str(CFB_event_data_json['scoringPlays'][play]['period']['number']) + ", " + CFB_event_data_json['scoringPlays'][play]['clock']['displayValue'] + "\n "
		except IndexError:
			continue
	if scoring_plays != "Scoring Plays:\n":
		scoring_plays = scoring_plays[:-2]
		
	#Build basic game info, stadium, teams, record, score, final status, headline if available

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

	#Add spaces in the first two lines output for the game so that scores are right-justified	
		
	visitor_len = len(visitor+" ("+visitor_record+") "+visitor_qtrs+" "+str(visitor_score))
	home_len = len(home+" ("+home_record+") "+home_qtrs+" "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	
	#Print game header, team, scores, etc.
	
	print(visitor, "("+visitor_record+") "+visitor_qtrs+"  "+visitor_add_spc, visitor_score)
	print(home, "("+home_record+") "+home_qtrs+"  "+home_add_spc, home_score, game_status, stadium)
	if notes != "":
		print(" "+notes)
	if headline != "":
		print (" "+headline)

	#Print game stats as available
	
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
	if scoring_plays != "Scoring Plays:\n":
		print(scoring_plays)
	print()

def CFB_in_progress(game_number):
	
	#Make event call for current game, game_number is parm passed into def
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())
	
	#Build home & visiting team stat lines, plus team in possession & drive stats
	
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
		
	#Build all player stats
	
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

	#Build basic game info, stadium, teams, record, score, last play, timeouts, down & distance, time remaining if available

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
	
	#Add spaces in the first two lines output for the game so that scores are right-justified	

	visitor_len = len(visitor+" ("+visitor_record+") " + str(visitor_timeouts) + " T/O  "+str(visitor_score))
	home_len = len (home+" ("+home_record+") "+str(home_timeouts)+" T/O  "+str(home_score))
	if visitor_len > home_len:
		visitor_add_spc = ""
		home_add_spc = " " * (visitor_len - home_len)
	else:
		home_add_spc = ""
		visitor_add_spc = " " * (home_len - visitor_len)
	
	#Print game header, team, scores, etc.
	
	print(visitor, "("+visitor_record+") " + str(visitor_timeouts) + " T/O   "+visitor_add_spc, visitor_score)    # str() nec b/c +'s with numbers
	print(home, "("+home_record+") "+str(home_timeouts)+" T/O   "+home_add_spc, home_score)
	if down_distance_ball_on != "":
		print (" "+down_distance_ball_on)
	print(" "+game_status, "\n", current_drive_possession+" Ball: "+current_drive, "\n", last_play)
	if notes != "":
		print(" " + notes)

	#Print game stats as available
	
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
	
	#Make event call for current game, game_number is parm passed into def
	#No injuries available
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=" + CFB_data_json['events'][game_number]['id']
	CFB_event = urlopen(url_event)
	CFB_event_data_json = json.loads(CFB_event.read())

	#Build basic game info, stadium, teams, record, weather, broadcast network, odds, over/under if available
	
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
		
	#Build visiting & home team stat averages
	
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
	else:                                                             #May be abbrev but no stats, header ok, other if's ok, line feed if blank ok
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
	
	#Build last 5 game results for both teams, most recent listed last
		
	home_previous_games = " Previous Games: "  #Last 5 games; for some Pythonic reason, the for loop stops 1 game too soon if range (0,4), even though the indices are in the range(0,4)?!
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
		
	#Print basic game info, then visiting & home team stats, leaders, injuries, & last 5 games

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

url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200"
CFB_today = urlopen(url)
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