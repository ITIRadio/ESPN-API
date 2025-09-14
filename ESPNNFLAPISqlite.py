from urllib.request import urlopen
import json
import sys
from datetime import datetime
import re
import sqlite3

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

def NFL_post_game(game_number):
	
	#Make event API call & transfer to dictionary. Note that the game number, or id, is passed into the def for the API call
	#In this API, visiting teams are listed 1st, not 2nd, as in the scoreboard API
	#For range loops build players until it runs out of players, and for loop is continued out of
	#There are far too many null data in this REST API, so try/except blocks are necessary & default to blanks as necessary
	
	url_event = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=" + NFL_data_json['events'][game_number]['id']
	NFL_event = urlopen(url_event)
	NFL_event_data_json = json.loads(NFL_event.read())
	
	try:                                      # Basic data
		home = NFL_event_data_json['boxscore']['teams'][1]['team']['abbreviation']
		visitor = NFL_event_data_json['boxscore']['teams'][0]['team']['abbreviation']
		home_score = int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][0]['score'])
		visitor_score = int(NFL_data_json['events'][game_number]['competitions'][0]['competitors'][1]['score'])
	except sqlite3.Error as err:              # If this fails, exit
		print("Insufficient data available to add to database.")
		if db_conn:
			db_conn.close()
		exit()
		
	try:                           # team_totals Table
		home_first_downs = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][0]['displayValue'])
		visitor_first_downs = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][0]['displayValue'])
		home_rushing_attempts = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][16]['displayValue'])
		visitor_rushing_attempts = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][16]['displayValue'])
		home_rushing_yds = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][15]['displayValue'])
		visitor_rushing_yds = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][15]['displayValue'])
		home_passing_yds = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][10]['displayValue'])
		visitor_passing_yds = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][10]['displayValue'])

		home_passing_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][11]['displayValue']
		home_passing_list = re.split(r'/', home_passing_string)
		home_passing_completed = int(home_passing_list[0])
		home_passing_attempted = int(home_passing_list[1])
		visitor_passing_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][11]['displayValue']
		visitor_passing_list = re.split(r'/', visitor_passing_string)
		visitor_passing_completed = int(visitor_passing_list[0])
		visitor_passing_attempted = int(visitor_passing_list[1])
		
		home_total_yds = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][7]['displayValue'])
		visitor_total_yds = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][7]['displayValue'])
		home_had_intercepted = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][13]['displayValue'])
		visitor_had_intercepted = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][13]['displayValue'])
		home_fumbles_lost = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][21]['displayValue'])
		visitor_fumbles_lost = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][21]['displayValue'])
		
		home_sacked_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][14]['displayValue']
		home_sacked_list = re.split(r'-', home_sacked_string)
		home_sacked = float(home_sacked_list[0])
		home_sacked_yds = int(home_sacked_list[1])
		visitor_sacked_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][14]['displayValue']
		visitor_sacked_list = re.split(r'-', visitor_sacked_string)
		visitor_sacked = float(visitor_sacked_list[0])
		visitor_sacked_yds = int(visitor_sacked_list[1])
		
		home_third_down_conversions_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][4]['displayValue']
		home_third_down_conversions_list = re.split(r'-', home_third_down_conversions_string)
		home_third_down_conversions_made = int(home_third_down_conversions_list[0])
		home_third_down_conversions_attempted = int(home_third_down_conversions_list[1])
		visitor_third_down_conversions_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][4]['displayValue']
		visitor_third_down_conversions_list = re.split(r'-', visitor_third_down_conversions_string)
		visitor_third_down_conversions_made = int(visitor_third_down_conversions_list[0])
		visitor_third_down_conversions_attempted = int(visitor_third_down_conversions_list[1])
		
		home_fourth_down_conversions_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][5]['displayValue']
		home_fourth_down_conversions_list = re.split(r'-', home_fourth_down_conversions_string)
		home_fourth_down_conversions_made = int(home_fourth_down_conversions_list[0])
		home_fourth_down_conversions_attempted = int(home_fourth_down_conversions_list[1])
		visitor_fourth_down_conversions_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][5]['displayValue']
		visitor_fourth_down_conversions_list = re.split(r'-', visitor_fourth_down_conversions_string)
		visitor_fourth_down_conversions_made = int(visitor_fourth_down_conversions_list[0])
		visitor_fourth_down_conversions_attempted = int(visitor_fourth_down_conversions_list[1])
		
		home_penalties_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][19]['displayValue']
		home_penalties_list = re.split(r'-', home_penalties_string)
		home_penalties = int(home_penalties_list[0])
		home_penalties_yds = int(home_penalties_list[1])
		visitor_penalties_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][19]['displayValue']
		visitor_penalties_list = re.split(r'-', visitor_penalties_string)
		visitor_penalties = int(visitor_penalties_list[0])
		visitor_penalties_yds = int(visitor_penalties_list[1])
		
		home_red_zone_string = NFL_event_data_json['boxscore']['teams'][1]['statistics'][18]['displayValue']
		home_red_zone_list = re.split(r'-', home_red_zone_string)
		home_red_zone_tds = int(home_red_zone_list[0])
		home_red_zone_trips = int(home_red_zone_list[1])
		visitor_red_zone_string = NFL_event_data_json['boxscore']['teams'][0]['statistics'][18]['displayValue']
		visitor_red_zone_list = re.split(r'-', visitor_red_zone_string)
		visitor_red_zone_tds = int(visitor_red_zone_list[0])
		visitor_red_zone_trips = int(visitor_red_zone_list[1])
		
		home_total_plays = int(NFL_event_data_json['boxscore']['teams'][1]['statistics'][6]['displayValue'])
		visitor_total_plays = int(NFL_event_data_json['boxscore']['teams'][0]['statistics'][6]['displayValue'])
		home_time_possession = str(NFL_event_data_json['boxscore']['teams'][1]['statistics'][24]['displayValue'])
		visitor_time_possession = str(NFL_event_data_json['boxscore']['teams'][0]['statistics'][24]['displayValue'])
		
		if home_score == visitor_score:
			home_winner = "T"
			visitor_winner = "T"
		elif home_score > visitor_score:
			home_winner = "W"
			visitor_winner = "L"
		else:
			home_winner = "L"
			visitor_winner = "W"
		
		insert_query = "REPLACE INTO team_totals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		insert_data = (home, game_date, visitor, "H", home_winner, home_score, visitor_score, home_first_downs, home_rushing_attempts, home_rushing_yds, home_passing_completed, home_passing_attempted, home_passing_yds, home_total_yds, home_had_intercepted, home_fumbles_lost, home_sacked, home_sacked_yds, home_third_down_conversions_made, home_third_down_conversions_attempted, home_fourth_down_conversions_made, home_fourth_down_conversions_attempted, home_penalties, home_penalties_yds, home_red_zone_tds, home_red_zone_trips, home_total_plays, home_time_possession)
		
		db_cursor.execute(insert_query, insert_data)
		
		insert_query = "REPLACE INTO team_totals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		insert_data = (visitor, game_date, home, "V", visitor_winner, visitor_score, home_score, visitor_first_downs, visitor_rushing_attempts, visitor_rushing_yds, visitor_passing_completed, visitor_passing_attempted, visitor_passing_yds, visitor_total_yds, visitor_had_intercepted, visitor_fumbles_lost, visitor_sacked, visitor_sacked_yds, visitor_third_down_conversions_made, visitor_third_down_conversions_attempted, visitor_fourth_down_conversions_made, visitor_fourth_down_conversions_attempted, visitor_penalties, visitor_penalties_yds, visitor_red_zone_tds, visitor_red_zone_trips, visitor_total_plays, visitor_time_possession)
		
		db_cursor.execute(insert_query, insert_data)
		
	except IndexError:
		print(home, visitor, "Team stat API error")
	except sqlite3.Error as err:
		print(home, visitor, "Team stat SQLite error")


	for player in range(0, 3):      # Home passing Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			passing_string = NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][0]
			passing_list = re.split(r'/', passing_string)
			completions = int(passing_list[0])
			attempts = int(passing_list[1])
			yards_passing = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][1])
			tds_passing = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][3])
			interceptions = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][0]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO passing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, completions, attempts, yards_passing, tds_passing, interceptions)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Passing stat error: ", err)
			
	for player in range(0, 3):      # Visitor passing Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			passing_string = NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][0]
			passing_list = re.split(r'/', passing_string)
			completions = int(passing_list[0])
			attempts = int(passing_list[1])
			yards_passing = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][1])
			tds_passing = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][3])
			interceptions = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][0]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO passing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, completions, attempts, yards_passing, tds_passing, interceptions)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Passing stat error: ", err)

	for player in range(0, 7):      # Home rushing Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			rushes = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][0])
			yards_rushing = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][1])
			tds_rushing = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][3])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][1]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO rushing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, rushes, yards_rushing, tds_rushing, long)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Rushing stat error: ", err)

	for player in range(0, 7):      # Visitor rushing Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			rushes = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][0])
			yards_rushing = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][1])
			tds_rushing = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][3])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][1]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO rushing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, rushes, yards_rushing, tds_rushing, long)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Rushing stat error: ", err)

	for player in range(0, 10):      # Home receiving Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			receptions = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][0])
			yards_receiving = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][1])
			tds_receiving = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][3])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][4])
			targets = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][2]['athletes'][player]['stats'][5])
			insert_query = "REPLACE INTO receiving VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, receptions, yards_receiving, tds_receiving, long, targets)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Receiving stat error: ", err)

	for player in range(0, 10):      # Visitor receiving Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			receptions = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][0])
			yards_receiving = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][1])
			tds_receiving = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][3])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][4])
			targets = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][2]['athletes'][player]['stats'][5])
			insert_query = "REPLACE INTO receiving VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, receptions, yards_receiving, tds_receiving, long, targets)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Receiving stat error: ", err)

	for player in range(0, 3):      # Home kicking Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][8]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][8]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			fg_string = NFL_event_data_json['boxscore']['players'][1]['statistics'][8]['athletes'][player]['stats'][0]
			fg_list = re.split(r'/', fg_string)
			fg_made = int(fg_list[0])
			fg_attempted = int(fg_list[1])
			xp_string = NFL_event_data_json['boxscore']['players'][1]['statistics'][8]['athletes'][player]['stats'][3]
			xp_list = re.split(r'/', xp_string)
			xp_made = int(xp_list[0])
			xp_attempted = int(xp_list[1])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][8]['athletes'][player]['stats'][2])
			insert_query = "REPLACE INTO kicking VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, fg_made, fg_attempted, xp_made, xp_attempted, long)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Kicking stat error: ", err)
			
	for player in range(0, 3):      # Visitor kicking Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][8]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][8]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			fg_string = NFL_event_data_json['boxscore']['players'][0]['statistics'][8]['athletes'][player]['stats'][0]
			fg_list = re.split(r'/', fg_string)
			fg_made = int(fg_list[0])
			fg_attempted = int(fg_list[1])
			xp_string = NFL_event_data_json['boxscore']['players'][0]['statistics'][8]['athletes'][player]['stats'][3]
			xp_list = re.split(r'/', xp_string)
			xp_made = int(xp_list[0])
			xp_attempted = int(xp_list[1])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][8]['athletes'][player]['stats'][2])
			insert_query = "REPLACE INTO kicking VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, fg_made, fg_attempted, xp_made, xp_attempted, long)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Kicking stat error: ", err)

	for player in range(0, 7):      # Home punting Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			punts = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][5])
			touchbacks = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][3])
			inside_20 = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][9]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO punting VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, punts, yds, long, touchbacks, inside_20)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Punting stat error: ", err)

	for player in range(0, 7):      # Visitor punting Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			punts = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][5])
			touchbacks = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][3])
			inside_20 = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][9]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO punting VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, punts, yds, long, touchbacks, inside_20)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Punting stat error: ", err)

	for player in range(0, 7):      # Home punt_returns Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			punt_returns = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][3])
			punt_return_tds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][7]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO punt_returns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, punt_returns, yds, long, punt_return_tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Punt return stat error: ", err)

	for player in range(0, 7):      # Visitor punt_returns Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			punt_returns = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][3])
			punt_return_tds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][7]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO punt_returns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, punt_returns, yds, long, punt_return_tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Punt return stat error: ", err)

	for player in range(0, 7):      # Home kickoff_returns Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			kickoff_returns = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][3])
			kickoff_return_tds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][6]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO kickoff_returns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, kickoff_returns, yds, long, kickoff_return_tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Kickoff return stat error: ", err)

	for player in range(0, 7):      # Visitor kickoff_returns Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			kickoff_returns = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][1])
			long = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][3])
			kickoff_return_tds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][6]['athletes'][player]['stats'][4])
			insert_query = "REPLACE INTO kickoff_returns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, kickoff_returns, yds, long, kickoff_return_tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Kickoff return stat error: ", err)

	for player in range(0, 7):      # Home interceptions Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			interceptions = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][1])
			interception_tds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][5]['athletes'][player]['stats'][2])
			insert_query = "REPLACE INTO interceptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, interceptions, interception_tds, yds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Interceptions stat error: ", err)

	for player in range(0, 7):      # Visitor interceptions Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			interceptions = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][0])
			yds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][1])
			interception_tds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][5]['athletes'][player]['stats'][2])
			insert_query = "REPLACE INTO interceptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, interceptions, interception_tds, yds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Interceptions stat error: ", err)

	for player in range(0, 7):      # Home fumbles Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][3]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][3]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			fumbles = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][3]['athletes'][player]['stats'][0])
			fumbles_lost = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][3]['athletes'][player]['stats'][1])
			insert_query = "REPLACE INTO fumbles VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, fumbles, fumbles_lost)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Fumbles stat error: ", err)

	for player in range(0, 7):      # Visitor fumbles Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][3]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][3]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			fumbles = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][3]['athletes'][player]['stats'][0])
			fumbles_lost = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][3]['athletes'][player]['stats'][1])
			insert_query = "REPLACE INTO fumbles VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, fumbles, fumbles_lost)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Fumbles stat error: ", err)

	for player in range(0, 40):      # Home individual_defense Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['athlete']['displayName']
			team_abbr = home
			opponent_abbr = visitor
			home_visitor = "H"
			tackles = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][0])
			solo = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][1])
			sacks = float(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][2])
			for_loss = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][3])
			passes_defensed = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][4])
			qb_hits = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][5])
			tds = int(NFL_event_data_json['boxscore']['players'][1]['statistics'][4]['athletes'][player]['stats'][6])
			insert_query = "REPLACE INTO individual_defense VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, tackles, solo, sacks, for_loss, passes_defensed, qb_hits, tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Individual defense stat error: ", err)

	for player in range(0, 40):      # Visitor individual_defense Table
		try:
			player_id = NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['athlete']['id']
			display_name = NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['athlete']['displayName']
			team_abbr = visitor
			opponent_abbr = home
			home_visitor = "V"
			tackles = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][0])
			solo = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][1])
			sacks = float(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][2])
			for_loss = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][3])
			passes_defensed = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][4])
			qb_hits = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][5])
			tds = int(NFL_event_data_json['boxscore']['players'][0]['statistics'][4]['athletes'][player]['stats'][6])
			insert_query = "REPLACE INTO individual_defense VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
			insert_data = (player_id, display_name, team_abbr, game_date, opponent_abbr, home_visitor, tackles, solo, sacks, for_loss, passes_defensed, qb_hits, tds)
			db_cursor.execute(insert_query, insert_data)
		except IndexError:
			continue
		except sqlite3.Error as err:
			print(home, visitor, "Individual defense stat error: ", err)

	
	try:
		db_conn.commit()
	except sqlite3.Error as err:   #If this fails, exit
		print("Commit error: err")
		if db_conn:
			db_conn.close()
		exit()
	

#Mainline

if len(sys.argv) == 2:
	date_arg = str(sys.argv[1])
	url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=" + date_arg + "-" + date_arg
	try:
		game_date = date_arg
		datetime.strptime(game_date, "%Y%m%d")                 # Checks for valid date (strptime overwrites date itself within call)
	except:
		print("Incorrect date format, use YYYYMMDD format.")
		exit()
else:
	print("Enter one day as a parameter, YYYYMMDD.")
	exit()

try:
	NFL_today = urlopen(url)
except:
	print("No games on this date.")         #If get past datetime above, date is OK, so API error due to no games.
	exit()

NFL_data_json = json.loads(NFL_today.read())

try:
	db_conn = sqlite3.connect('NFLStats2025.db')
	db_cursor = db_conn.cursor()
except sqlite3.Error as err:
	print("Database doesn't exist or error in opening")
	exit()

for game in range(0, 20):
	try: 
		game_state = NFL_data_json['events'][game]['status']['type']['state']
		if game_state == "post":
			NFL_post_game(game)             #Skip games not completed, if run twice vs same date, primary key replacement/overwrite will occur
	except IndexError:
		continue
if db_conn:
	db_conn.close()