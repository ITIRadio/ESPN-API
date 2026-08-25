import sqlite3
import os
import sys

if len(sys.argv) == 2:
	db_file_name = str(sys.argv[1])
else:
	print("Use one parameter, a new .sqlite file name.")
	exit()
if os.path.isfile(db_file_name):
	print("File already exists. Use new file name as this process destroys data.")
	exit()
try:
	db_conn = sqlite3.connect(db_file_name)
	db_cursor = db_conn.cursor()
except sqlite3.Error as err:
	print("Database creation error.")
	exit()

try:

	create_table = '''
	CREATE TABLE IF NOT EXISTS passing (
		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		completions INTEGER NOT NULL,
		attempts INTEGER NOT NULL,
		yards_passing INTEGER NOT NULL,
		tds_passing INTEGER NOT NULL, 
		interceptions INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)

	create_table = '''
	CREATE TABLE IF NOT EXISTS rushing (
		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		rushes INTEGER NOT NULL,
		yards_rushing INTEGER NOT NULL,
		tds_rushing INTEGER NOT NULL, 
		long INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)

	create_table = '''
	CREATE TABLE IF NOT EXISTS receiving (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		receptions INTEGER NOT NULL,
		yards_receiving INTEGER NOT NULL,
		tds_receiving INTEGER NOT NULL, 
		long INTEGER NOT NULL,
		targets INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)

	create_table = '''
	CREATE TABLE IF NOT EXISTS kicking (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		fg_made INTEGER NOT NULL,
		fg_attempted INTEGER NOT NULL,
		xp_made INTEGER NOT NULL, 
		xp_attempted INTEGER NOT NULL,
		long INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS punting (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		punts INTEGER NOT NULL,
		yds INTEGER NOT NULL,
		long INTEGER NOT NULL,
		touchbacks INTEGER NOT NULL,
		inside_20 INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS punt_returns (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		punt_returns INTEGER NOT NULL,
		yds INTEGER NOT NULL,
		long INTEGER NOT NULL,
		punt_return_tds INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS kickoff_returns (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		kickoff_returns INTEGER NOT NULL,
		yds INTEGER NOT NULL,
		long INTEGER NOT NULL,
		kick_return_tds INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS interceptions (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		interceptions INTEGER NOT NULL,
		interception_tds INTEGER NOT NULL,
		yds INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS fumbles (
 		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		fumbles INTEGER NOT NULL,
		fumbles_lost INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS individual_defense (
		player_id INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		tackles INTEGER NOT NULL,
		solo INTEGER NOT NULL,
		sacks REAL NOT NULL,
		for_loss INTEGER NOT NULL, 
		passes_defensed INTEGER NOT NULL,
		qb_hits INTEGER NOT NULL,
		tds INTEGER NOT NULL,
		ff INTEGER NOT NULL,
		fr INTEGER NOT NULL,
		PRIMARY KEY (player_id, game_date)
	);
	'''
	db_cursor.execute(create_table)
	
	create_table = '''
	CREATE TABLE IF NOT EXISTS team_totals (
		team_abbr TEXT NOT NULL,
		full_name TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		win_loss TEXT NOT NULL,
		pts_for INTEGER NOT NULL,
		pts_against INTEGER NOT NULL,
		first_downs INTEGER NOT NULL,
		rushing_attempts INTEGER NOT NULL, 
		rushing_yds INTEGER NOT NULL,
		passing_completed INTEGER NOT NULL,
		passing_attempted INTEGER NOT NULL,
		passing_yds INTEGER NOT NULL,
		total_yds INTEGER NOT NULL,
		had_intercepted INTEGER NOT NULL,
		fumbles_lost INTEGER NOT NULL,
		sacked REAL NOT NULL,
		sacked_yds INTEGER NOT NULL,
		third_down_conversions_made INTEGER NOT NULL,
		third_down_conversions_attempted INTEGER NOT NULL,
		fourth_down_conversions_made INTEGER NOT NULL,
		fourth_down_conversions_attempted INTEGER NOT NULL,
		penalties INTEGER NOT NULL,
		penalty_yds INTEGER NOT NULL,
		red_zone_tds INTEGER NOT NULL,
		red_zone_trips INTEGER NOT NULL,
		total_plays INTEGER NOT NULL,
		time_possession TEXT NOT NULL,
		PRIMARY KEY (team_abbr, game_date)
	);
	'''
	db_cursor.execute(create_table)	

	create_table = '''
	CREATE TABLE IF NOT EXISTS scoring_plays (
		team_abbr TEXT NOT NULL,
		game_date TEXT NOT NULL,
		opponent_abbr TEXT NOT NULL,
		home_visitor TEXT NOT NULL,
		play_descr TEXT NOT NULL,
		qtr INTEGER NOT NULL,
		play_time TEXT NOT NULL
	);
	'''
	db_cursor.execute(create_table)
	
	db_conn.commit()

	print("Blank database successfully created.")

except sqlite3.Error as err:
	print(f"Error creating table: {err}")

finally:
	if db_conn:
		db_conn.close()

