import sqlite3
from rich.console import Console
from rich.table import Table
from datetime import datetime

#This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

today_date = datetime.now()
today = today_date.strftime("%B %d, %Y")

console = Console()

try:
	db_conn = sqlite3.connect('NFLStats2025.db')
	team_cursor = db_conn.cursor()
	individ_cursor = db_conn.cursor()
	gm_cursor = db_conn.cursor()
	int_cursor = db_conn.cursor()
except sqlite3.Error as err:
	print("Database doesn't exist or error in opening")
	exit()

team_cursor.execute("SELECT DISTINCT team_abbr, full_name FROM team_totals ORDER BY full_name")

for team_row in team_cursor:
	
	abbr = team_row[0]
	full_team_name = team_row[1]
	
	print(full_team_name + " Individual Game Statistics Report as of " + today)
	
# Individual Passing

	print()
	print("Passing")
	print()

	qry = """SELECT DISTINCT display_name, player_id
			FROM passing
			WHERE team_abbr = ?"""
	individ_cursor.execute(qry, (abbr,))
	
	for individ_row in individ_cursor:
		
		name = individ_row[0]
		plyr_id = individ_row[1]
		
		qry = """SELECT game_date, opponent_abbr, home_visitor, completions, attempts, yards_passing, tds_passing, interceptions
				FROM passing
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
		
		qry_table = Table(box=None, header_style="default")
		qry_table.add_column(name)
		qry_table.add_column("")
		qry_table.add_column("")
		qry_table.add_column("Comp", justify="right")
		qry_table.add_column("Att", justify="right")
		qry_table.add_column("Pct", justify="right")
		qry_table.add_column("Yds", justify="right")
		qry_table.add_column("TD", justify="right")
		qry_table.add_column("Int", justify="right")
		
		ttl_comp = ttl_att = ttl_yds = ttl_td = ttl_int = 0
		
		for gm_row in gm_cursor:
			game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
			game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
			at_vs = "@" if gm_row[2] == "V" else "vs"
			comp_pct = gm_row[3] / gm_row[4] if gm_row[4] > 0 else 0
			qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), f"{comp_pct:2.1%}", str(gm_row[5]), str(gm_row[6]), str(gm_row[7]))
			ttl_comp += gm_row[3]; ttl_att += gm_row[4]; ttl_yds += gm_row[5]; ttl_td += gm_row[6]; ttl_int += gm_row[7] 
			
		ttl_pct = ttl_comp / ttl_att if ttl_att > 0 else 0
		qry_table.add_row("Totals", "", "", str(ttl_comp), str(ttl_att), f"{ttl_pct:2.1%}", str(ttl_yds), str(ttl_td), str(ttl_int))
		console.print(qry_table)
		print()
		
# Individual Rushing

	print("----------------------------------------------------------------------")
	print("Rushing and Receiving (Rushers First)")
	print()
	
	qry = """SELECT DISTINCT display_name, player_id
			FROM rushing
			WHERE team_abbr = ?"""
	individ_cursor.execute(qry, (abbr,))
	
	for individ_row in individ_cursor:
		
		name = individ_row[0]
		plyr_id = individ_row[1]
		
		print(name)
		print()
		
		qry = """SELECT game_date, opponent_abbr, home_visitor, rushes, yards_rushing, tds_rushing, long
				FROM rushing
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
		
		qry_table = Table(box=None, header_style="default")
		qry_table.add_column("Rushing")
		qry_table.add_column("")
		qry_table.add_column("")
		qry_table.add_column("Carries", justify="right")
		qry_table.add_column("Yds", justify="right")
		qry_table.add_column("Yds/Rush", justify="right")
		qry_table.add_column("TD", justify="right")
		qry_table.add_column("Long", justify="right")
		
		ttl_rush = ttl_yds = ttl_td = long = 0
		
		for gm_row in gm_cursor:
			game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
			game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
			at_vs = "@" if gm_row[2] == "V" else "vs"
			yds_per_rush = gm_row[4] / gm_row[3] if gm_row[3] > 0 else 0
			qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), f"{yds_per_rush:.1f}", str(gm_row[5]), str(gm_row[6]))
			ttl_rush += gm_row[3]; ttl_yds += gm_row[4]; ttl_td += gm_row[5]; long = gm_row[6] if gm_row[6] > long else long
		
		yds_per_rush = ttl_yds / ttl_rush if ttl_rush >  0 else 0
		qry_table.add_row("Totals", "", "", str(ttl_rush), str(ttl_yds), f"{yds_per_rush:.1f}", str(ttl_td), str(long))
		console.print(qry_table)
		print()
		
		qry = """SELECT game_date, opponent_abbr, home_visitor, receptions, yards_receiving, tds_receiving, long, targets
				FROM receiving
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
		
		test_retn = gm_cursor.fetchone()
		
		if test_retn != None:                     #If a rusher does not have a reception, skip 2nd table
			gm_cursor.execute(qry, (plyr_id,))
		
			qry_table = Table(box=None, header_style="default")
			qry_table.add_column("Receiving")
			qry_table.add_column("")
			qry_table.add_column("")
			qry_table.add_column("Recept", justify="right")
			qry_table.add_column("Yds", justify="right")
			qry_table.add_column("Yds/Recept", justify="right")
			qry_table.add_column("TD", justify="right")
			qry_table.add_column("Long", justify="right")
			qry_table.add_column("Tgt", justify="right")
			
			ttl_recept = ttl_yds = ttl_td = long = ttl_tgt = 0
		
			for gm_row in gm_cursor:
				game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
				game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
				at_vs = "@" if gm_row[2] == "V" else "vs"
				yds_per_recept = gm_row[4] / gm_row[3] if gm_row[3] > 0 else 0
				qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), f"{yds_per_recept:.1f}", str(gm_row[5]), str(gm_row[6]), str(gm_row[7]))
				ttl_recept += gm_row[3]; ttl_yds += gm_row[4]; ttl_td += gm_row[5]; long = gm_row[6] if gm_row[6] > long else long; ttl_tgt += gm_row[7]

			yds_per_recept = ttl_yds / ttl_recept if ttl_recept >  0 else 0
			qry_table.add_row("Totals", "", "", str(ttl_rush), str(ttl_yds), f"{yds_per_recept:.1f}", str(ttl_td), str(long), str(ttl_tgt))
			console.print(qry_table)
			print()

# Individual Receiving Not In Rushing

	qry = """SELECT DISTINCT receiving.display_name, receiving.player_id
			FROM receiving LEFT JOIN rushing on receiving.player_id = rushing.player_id
			WHERE rushing.player_id IS NULL AND receiving.team_abbr = ?"""
	individ_cursor.execute(qry, (abbr,))
	
	for individ_row in individ_cursor:
		
		name = individ_row[0]
		plyr_id = individ_row[1]
		
		print(name)
		print()
		
		qry = """SELECT game_date, opponent_abbr, home_visitor, receptions, yards_receiving, tds_receiving, long, targets
				FROM receiving
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
	
		qry_table = Table(box=None, header_style="default")
		qry_table.add_column("Receiving")
		qry_table.add_column("")
		qry_table.add_column("")
		qry_table.add_column("Recept", justify="right")
		qry_table.add_column("Yds", justify="right")
		qry_table.add_column("Yds/Recept", justify="right")
		qry_table.add_column("TD", justify="right")
		qry_table.add_column("Long", justify="right")
		qry_table.add_column("Tgt", justify="right")
		
		tl_recept = ttl_yds = ttl_td = long = ttl_tgt = 0
	
		for gm_row in gm_cursor:
			game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
			game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
			at_vs = "@" if gm_row[2] == "V" else "vs"
			yds_per_recept = gm_row[4] / gm_row[3] if gm_row[3] > 0 else 0
			qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), f"{yds_per_recept:.1f}", str(gm_row[5]), str(gm_row[6]), str(gm_row[7]))
			ttl_recept += gm_row[3]; ttl_yds += gm_row[4]; ttl_td += gm_row[5]; long = gm_row[6] if gm_row[6] > long else long; ttl_tgt += gm_row[7]
		
		yds_per_recept = ttl_yds / ttl_recept if ttl_recept >  0 else 0
		qry_table.add_row("Totals", "", "", str(ttl_rush), str(ttl_yds), f"{yds_per_recept:.1f}", str(ttl_td), str(long), str(ttl_tgt))
		console.print(qry_table)
		print()

# Kicking

	print("----------------------------------------------------------------------")
	print("Kicking")
	print()
	
	qry = """SELECT DISTINCT display_name, player_id
			FROM kicking
			WHERE team_abbr = ?"""
	individ_cursor.execute(qry, (abbr,))
	
	for individ_row in individ_cursor:
		
		name = individ_row[0]
		plyr_id = individ_row[1]
	
		qry = """SELECT game_date, opponent_abbr, home_visitor, fg_made, fg_attempted, long, xp_made, xp_attempted
				FROM kicking
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
		
		qry_table = Table(box=None, header_style="default")
		qry_table.add_column(name)
		qry_table.add_column("")
		qry_table.add_column("")
		qry_table.add_column("FG Made", justify="right")
		qry_table.add_column("FG Att", justify="right")
		qry_table.add_column("Pct", justify="right")
		qry_table.add_column("Long", justify="right")
		qry_table.add_column("XP Made", justify="right")
		qry_table.add_column("XP Att", justify="right")
		qry_table.add_column("Pct", justify="right")
		
		ttl_fg_made = ttl_fg_att = long = ttl_xp_made = ttl_xp_att = 0

		for gm_row in gm_cursor:
			game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
			game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
			at_vs = "@" if gm_row[2] == "V" else "vs"
			fg_pct = gm_row[3] / gm_row[4] if gm_row[4] > 0 else 0
			xp_pct = gm_row[6] / gm_row[7] if gm_row[7] > 0 else 0
			qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), f"{fg_pct:2.1%}", str(gm_row[5]), str(gm_row[6]), str(gm_row[7]), f"{xp_pct:2.1%}")
			ttl_fg_made += gm_row[3]; ttl_fg_att += gm_row[4]; long = gm_row[5] if gm_row[5] > long else long; ttl_xp_made += gm_row[6]; ttl_xp_att += gm_row[7]
		
		ttl_fg_pct = ttl_fg_made / ttl_fg_att if ttl_fg_att >  0 else 0
		ttl_xp_pct = ttl_xp_made / ttl_xp_att if ttl_xp_att >  0 else 0
		qry_table.add_row("Totals", "", "", str(ttl_fg_made), str(ttl_fg_att), f"{ttl_fg_pct:2.1%}", str(long), str(ttl_xp_made), str(ttl_xp_att), f"{ttl_xp_pct:2.1%}")
		console.print(qry_table)
		print()
		
# Individual Defense

	print("----------------------------------------------------------------------")
	print("Defense")
	print()
	
	qry = """SELECT DISTINCT display_name, player_id
			FROM individual_defense
			WHERE team_abbr = ?"""
	individ_cursor.execute(qry, (abbr,))
	
	for individ_row in individ_cursor:
		
		name = individ_row[0]
		plyr_id = individ_row[1]
		
		qry = """SELECT game_date, opponent_abbr, home_visitor, tackles, solo, sacks, for_loss, passes_defensed, qb_hits, tds
				FROM individual_defense
				WHERE player_id = ?
				ORDER BY game_date ASC"""
		gm_cursor.execute(qry, (plyr_id,))
		
		qry_table = Table(box=None, header_style="default")
		qry_table.add_column(name)
		qry_table.add_column("")
		qry_table.add_column("")
		qry_table.add_column("Tkls", justify="right")
		qry_table.add_column("Solos", justify="right")
		qry_table.add_column("Sacks", justify="right")
		qry_table.add_column("Int", justify="right")
		qry_table.add_column("Int Retn Yds", justify="right")
		qry_table.add_column("TFL", justify="right")
		qry_table.add_column("PD", justify="right")
		qry_table.add_column("QB Hit", justify="right")
		qry_table.add_column("TD", justify="right")
		
		ttl_tkl = ttl_solo = ttl_sack = ttl_int = ttl_retn_yds = ttl_for_loss = ttl_pd = ttl_qb_hit = ttl_td = 0
		
		for gm_row in gm_cursor:
			game_date_dt = datetime.strptime(gm_row[0], "%Y%m%d")
			game_date = game_date_dt.strftime("%b") + " " + game_date_dt.strftime("%-d")
			at_vs = "@" if gm_row[2] == "V" else "vs"
			
			qry = """SELECT SUM(interceptions), SUM(yds)
					FROM interceptions
					WHERE player_id = ? and game_date = ?"""
			int_cursor.execute(qry, (plyr_id,gm_row[0],))
			int_retn = int_cursor.fetchone()
		
			if int_retn[0] == None:
				qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), str(gm_row[5]), "0", "0", str(gm_row[6]), str(gm_row[7]), str(gm_row[8]), str(gm_row[9]))
				ttl_tkl += gm_row[3]; ttl_solo += gm_row[4]; ttl_sack += gm_row[5]; ttl_for_loss += gm_row[6]; ttl_pd += gm_row[7]; ttl_qb_hit += gm_row[8]; ttl_td += gm_row[9]
			else:
				qry_table.add_row(game_date, at_vs, gm_row[1], str(gm_row[3]), str(gm_row[4]), str(gm_row[5]), str(int_retn[0]), str(int_retn[1]),     str(gm_row[6]), str(gm_row[7]), str(gm_row[8]), str(gm_row[9]))
				ttl_tkl += gm_row[3]; ttl_solo += gm_row[4]; ttl_sack += gm_row[5]; ttl_for_loss += gm_row[6]; ttl_pd += gm_row[7]; ttl_qb_hit += gm_row[8]; ttl_td += gm_row[9]; ttl_int += int_retn[0]; ttl_retn_yds += int_retn[1]		

		qry_table.add_row("Totals", "", "", str(ttl_tkl), str(ttl_solo), str(ttl_sack), str(ttl_int), str(ttl_retn_yds), str(ttl_for_loss), str(ttl_pd), str(ttl_qb_hit), str(ttl_td))
		console.print(qry_table)
		print()
		
	print("\f")
		
		
db_conn.close()