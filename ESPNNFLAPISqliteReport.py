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
	qry_cursor = db_conn.cursor()
except sqlite3.Error as err:
	print("Database doesn't exist or error in opening")
	exit()

team_cursor.execute("SELECT DISTINCT team_abbr, full_name FROM team_totals ORDER BY full_name")

for team_row in team_cursor:
	
	abbr = team_row[0]
	full_team_name = team_row[1]
	
	print(full_team_name + " Statistics Report as of " + today)
	
# Team Summary & Results
	
	qry = "SELECT COUNT(*) FROM team_totals WHERE team_abbr = ? and win_loss = 'W'"    #Single quote for "W" within qry string
	qry_cursor.execute(qry, (abbr,))
	qry_row = qry_cursor.fetchone()
	wins = qry_row[0]
	qry = "SELECT COUNT(*) FROM team_totals WHERE team_abbr = ? and win_loss = 'L'"
	qry_cursor.execute(qry, (abbr,))
	qry_row = qry_cursor.fetchone()
	losses = qry_row[0]
	qry = "SELECT COUNT(*) FROM team_totals WHERE team_abbr = ? and win_loss = 'T'"
	qry_cursor.execute(qry, (abbr,))
	qry_row = qry_cursor.fetchone()
	ties = qry_row[0]
	num_gms = wins + losses + ties
	
	print(str(wins) + " Wins, " + str(losses) + " Losses, " + str(ties) + " Ties")
	print()
	
	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Results")
	qry_table.add_column("")
	qry_table.add_column("")
	qry_table.add_column("")
	qry_table.add_column("PF", justify="right")
	qry_table.add_column("PA", justify="right")
	
	qry = """SELECT game_date, opponent_abbr, home_visitor, win_loss, pts_for, pts_against
		FROM team_totals
		WHERE team_abbr = ?
		ORDER BY game_date"""
	qry_cursor.execute(qry, (abbr,))
	pts_for = pts_vs = 0
	
	for qry_row in qry_cursor:
		game_date_string = qry_row[0]
		game_date_dt = datetime.strptime(game_date_string, "%Y%m%d")    #YYYYMMDD string to datetime object
		game_date = game_date_dt.strftime("%B") + " " + game_date_dt.strftime("%-d")
		home_road = "Vs" if qry_row[2] == "H" else "@"
		qry_table.add_row(game_date, home_road, qry_row[1], qry_row[3], str(qry_row[4]), str(qry_row[5]))
		pts_for += qry_row[4]; pts_vs += qry_row[5]
	
	avg_pts_for = pts_for / num_gms
	avg_pts_vs = pts_vs / num_gms
	qry_table.add_row("Totals", "", "", "", str(pts_for), str(pts_vs))
	qry_table.add_row("Per Game", "", "", "", f"{avg_pts_for:.1f}", f"{avg_pts_vs:.1f}")
	console.print(qry_table)
	print()
	
# Team Statistics Totals Section

	qry_off = """SELECT SUM(first_downs),
				SUM(rushing_attempts),
				SUM(rushing_yds),
				SUM(passing_completed),
				SUM(passing_attempted),
				SUM(passing_yds),
				SUM(total_yds),
				SUM(had_intercepted),
				SUM(fumbles_lost),
				SUM(sacked),
				SUM(sacked_yds),
				SUM(third_down_conversions_made),
				SUM(third_down_conversions_attempted),
				SUM(fourth_down_conversions_made),
				SUM(fourth_down_conversions_attempted),
				SUM(penalties),
				SUM(penalty_yds),
				SUM(red_zone_tds),
				SUM(red_zone_trips),
				SUM(total_plays)
				FROM team_totals 
				WHERE team_abbr = ?"""
	
	qry_def = """SELECT SUM(first_downs),
				SUM(rushing_attempts),
				SUM(rushing_yds),
				SUM(passing_completed),
				SUM(passing_attempted),
				SUM(passing_yds),
				SUM(total_yds),
				SUM(had_intercepted),
				SUM(fumbles_lost),
				SUM(sacked),
				SUM(sacked_yds),
				SUM(third_down_conversions_made),
				SUM(third_down_conversions_attempted),
				SUM(fourth_down_conversions_made),
				SUM(fourth_down_conversions_attempted),
				SUM(penalties),
				SUM(penalty_yds),
				SUM(red_zone_tds),
				SUM(red_zone_trips),
				SUM(total_plays)
				FROM team_totals 
				WHERE opponent_abbr = ?"""
	
	qry_cursor.execute(qry_off, (abbr,))
	off_totals = qry_cursor.fetchone()
	qry_cursor.execute(qry_def, (abbr,))
	def_totals = qry_cursor.fetchone()
	
	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Team Statistics")
	qry_table.add_column("Offense", justify="right")
	qry_table.add_column("Per Game", justify="right")
	qry_table.add_column("Defense", justify="right")
	qry_table.add_column("Per Game", justify="right")
	off_result = off_totals[0] / num_gms
	def_result = def_totals[0] / num_gms
	qry_table.add_row("First Downs", str(off_totals[0]), f"{off_result:.1f}", str(def_totals[0]), f"{def_result:.1f}")
	off_result = off_totals[1] / num_gms
	def_result = def_totals[1] / num_gms
	qry_table.add_row("Rushes", str(off_totals[1]), f"{off_result:.1f}", str(def_totals[1]), f"{def_result:.1f}")
	off_result = off_totals[2] / num_gms
	def_result = def_totals[2] / num_gms
	qry_table.add_row("Rushing Yards", str(off_totals[2]), f"{off_result:.1f}", str(def_totals[2]), f"{def_result:.1f}")
	off_result = off_totals[2] / off_totals[1]
	def_result = def_totals[2] / def_totals[1]
	qry_table.add_row("  Yards Per Rush", f"{off_result:.1f}", "", f"{def_result:.1f}", "")
	qry_table.add_row("")
	off_result = off_totals[3] / num_gms
	def_result = def_totals[3] / num_gms
	qry_table.add_row("Passes Completed", str(off_totals[3]), f"{off_result:.1f}", str(def_totals[3]), f"{def_result:.1f}")
	off_result = off_totals[4] / num_gms
	def_result = def_totals[4] / num_gms
	qry_table.add_row("Passes Attempted", str(off_totals[4]), f"{off_result:.1f}", str(def_totals[4]), f"{def_result:.1f}")
	off_result = off_totals[3] / off_totals[4]
	def_result = def_totals[3] / def_totals[4]
	qry_table.add_row("  Completion Percent", f"{off_result:2.1%}", "", f"{def_result:2.1%}", "")
	off_result = off_totals[5] / num_gms
	def_result = def_totals[5] / num_gms
	qry_table.add_row("Net Passing Yds (Minus Sack Yds)", str(off_totals[5]), f"{off_result:.1f}", str(def_totals[5]), f"{def_result:.1f}")
	off_result = off_totals[5] / off_totals[3]
	def_result = def_totals[5] / def_totals[3]
	qry_table.add_row("  Net Yards Per Completion", f"{off_result:.1f}", "", f"{def_result:.1f}", "")
	off_result = off_totals[5] / off_totals[4]
	def_result = def_totals[5] / def_totals[4]
	qry_table.add_row("  Net Yards Per Attempt", f"{off_result:.1f}", "", f"{def_result:.1f}", "")
	off_result = off_totals[6] / num_gms
	def_result = def_totals[6] / num_gms
	qry_table.add_row("Total Yards", str(off_totals[6]), f"{off_result:.1f}", str(def_totals[6]), f"{def_result:.1f}")
	qry_table.add_row("")
	off_result = off_totals[7] / num_gms
	def_result = def_totals[7] / num_gms
	qry_table.add_row("Had Intercepted", str(off_totals[7]), f"{off_result:.1f}", str(def_totals[7]), f"{def_result:.1f}")
	off_result = off_totals[8] / num_gms
	def_result = def_totals[8] / num_gms
	qry_table.add_row("Fumbles Lost", str(off_totals[8]), f"{off_result:.1f}", str(def_totals[8]), f"{def_result:.1f}")
	off_result = off_totals[7] + off_totals[8]
	def_result = def_totals[7] + def_totals[8]
	qry_table.add_row("  Giveaways/Takeaways", str(off_result), "", str(def_result), "")
	off_result = def_totals[7] + def_totals[8] - (off_totals[8] + off_totals[7])
	qry_table.add_row("  Turnover Ratio", f"{off_result:{'+' if off_result > 0 else '-' if off_result < 0 else ''}}", "", "", "")
	qry_table.add_row("")
	off_result = off_totals[9] / num_gms
	def_result = def_totals[9] / num_gms
	qry_table.add_row("Sacked", str(off_totals[9]), f"{off_result:.1f}", str(def_totals[9]), f"{def_result:.1f}")
	off_result = off_totals[10] / num_gms
	def_result = def_totals[10] / num_gms
	qry_table.add_row("Sacked Yards", str(off_totals[10]), f"{off_result:.1f}", str(def_totals[10]), f"{def_result:.1f}")
	off_result = off_totals[10] / off_totals[9]
	def_result = def_totals[10] / def_totals[9]
	qry_table.add_row("  Yards Per Sack", f"{off_result:.1f}", "", f"{def_result:.1f}", "")
	qry_table.add_row("")
	off_result = off_totals[11] / num_gms
	def_result = def_totals[11] / num_gms
	qry_table.add_row("Third Down Conversions Made", str(off_totals[11]), f"{off_result:.1f}", str(def_totals[11]), f"{def_result:.1f}")
	off_result = off_totals[12] / num_gms
	def_result = def_totals[12] / num_gms
	qry_table.add_row("Third Down Conversions Attempted", str(off_totals[12]), f"{off_result:.1f}", str(def_totals[12]), f"{def_result:.1f}")
	off_result = off_totals[11] / off_totals[12]
	def_result = def_totals[11] / def_totals[12]
	qry_table.add_row("  Third Down Conv. Percent", f"{off_result:2.1%}", "", f"{def_result:2.1%}", "")
	off_result = off_totals[13] / num_gms
	def_result = def_totals[13] / num_gms
	qry_table.add_row("Fourth Down Conversions Made", str(off_totals[13]), f"{off_result:.1f}", str(def_totals[13]), f"{def_result:.1f}")
	off_result = off_totals[14] / num_gms
	def_result = def_totals[14] / num_gms
	qry_table.add_row("Fourth Down Conversions Attempted", str(off_totals[14]), f"{off_result:.1f}", str(def_totals[14]), f"{def_result:.1f}")
	if off_totals[14] != 0:
		off_result = off_totals[13] / off_totals[14]
	else:
		off_result = 0
	if def_totals[14] != 0:
		def_result = def_totals[13] / def_totals[14]
	else:
		def_result = 0
	qry_table.add_row("  Fourth Down Conv. Percent", f"{off_result:2.1%}", "", f"{def_result:2.1%}", "")
	qry_table.add_row("")
	off_result = off_totals[15] / num_gms
	def_result = def_totals[15] / num_gms
	qry_table.add_row("Penalties", str(off_totals[15]), f"{off_result:.1f}", str(def_totals[15]), f"{def_result:.1f}")
	off_result = off_totals[16] / num_gms
	def_result = def_totals[16] / num_gms
	qry_table.add_row("Penalty Yards", str(off_totals[16]), f"{off_result:.1f}", str(def_totals[16]), f"{def_result:.1f}")
	off_result = off_totals[17] / num_gms
	def_result = def_totals[17] / num_gms
	qry_table.add_row("")
	qry_table.add_row("Red Zone Touchdowns", str(off_totals[17]), f"{off_result:.1f}", str(def_totals[17]), f"{def_result:.1f}")
	off_result = off_totals[18] / num_gms
	def_result = def_totals[18] / num_gms
	qry_table.add_row("Red Zone Trips", str(off_totals[18]), f"{off_result:.1f}", str(def_totals[18]), f"{def_result:.1f}")
	off_result = off_totals[17] / off_totals[18]
	def_result = def_totals[17] / def_totals[18]
	qry_table.add_row("  Red Zone Conversion Percent", f"{off_result:2.1%}", "", f"{def_result:2.1%}", "")
	qry_table.add_row("")
	off_result = off_totals[19] / num_gms
	def_result = def_totals[19] / num_gms
	qry_table.add_row("Total Plays", str(off_totals[19]), f"{off_result:.1f}", str(def_totals[19]), f"{def_result:.1f}")
	off_result = off_totals[6] / off_totals[19]
	def_result = def_totals[6] / def_totals[19]
	qry_table.add_row("  Yards Per Play", f"{off_result:.1f}", "", f"{def_result:.1f}", "")
	
	console.print(qry_table)
	print()
	
# Individual Passing

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Passing")
	qry_table.add_column("Gms", justify="right")
	qry_table.add_column("Comp", justify="right")
	qry_table.add_column("Att", justify="right")
	qry_table.add_column("Pct", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Gm", justify="right")
	qry_table.add_column("TD", justify="right")
	qry_table.add_column("Int", justify="right")
	qry_table.add_column("300+", justify="right")
	
	qry = """SELECT display_name, SUM(completions) AS ttl_comp, SUM(attempts), SUM(yards_passing) AS yds, SUM(tds_passing), SUM(interceptions), COUNT(*) as gms, COUNT(CASE WHEN yards_passing > 299 THEN 1 END)
			FROM passing
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY yds DESC, ttl_comp DESC"""
	qry_cursor.execute(qry, (abbr,))
	comp = att = yds = td = int = t300 = 0
	
	for qry_row in qry_cursor:
		if qry_row[2] > 0:                                 # ESPN has QB's having a passing entry in games where 1 appears just to hand off
			comp_pct = qry_row[1] / qry_row[2]
			yds_per_gm = qry_row[3] / qry_row[6]
			qry_table.add_row(qry_row[0], str(qry_row[6]), str(qry_row[1]), str(qry_row[2]), f"{comp_pct:2.1%}", str(qry_row[3]), f"{yds_per_gm:.1f}", str(qry_row[4]), str(qry_row[5]), str(qry_row[7]))
			comp += qry_row[1]; att += qry_row[2]; yds += qry_row[3]; td += qry_row[4]; int += qry_row[5]; t300 += qry_row[7]
	
	ttl_comp_pct = comp / att
	ttl_yds_per_gm = yds / num_gms
	qry_table.add_row("Totals", "", str(comp), str(att), f"{ttl_comp_pct:2.1%}", str(yds), f"{ttl_yds_per_gm:.1f}", str(td), str(int), str(t300))
	console.print(qry_table)
	print()

# Individual Rushing

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Rushing")
	qry_table.add_column("Gms", justify="right")
	qry_table.add_column("Carries", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Rush", justify="right")
	qry_table.add_column("Yds/Gm", justify="right")
	qry_table.add_column("TD", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("100+", justify="right")
	
	qry = """SELECT display_name, SUM(rushes) AS ttl_rush, SUM(yards_rushing) AS yds, SUM(tds_rushing), MAX(long), COUNT(*) as gms, COUNT(CASE WHEN yards_rushing > 99 THEN 1 END)
			FROM rushing
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY yds DESC, ttl_rush DESC"""
	qry_cursor.execute(qry, (abbr,))
	rush = yds = td = h100 = long = 0
	
	for qry_row in qry_cursor:
		if qry_row[1] > 0:
			yds_per_gm = qry_row[2] / qry_row[5]
			yds_per_rush = qry_row[2] / qry_row[1]
			qry_table.add_row(qry_row[0], str(qry_row[5]), str(qry_row[1]), str(qry_row[2]), f"{yds_per_rush:.1f}", f"{yds_per_gm:.1f}", str(qry_row[3]), str(qry_row[4]), str(qry_row[6]))
			rush += qry_row[1]; yds += qry_row[2]; td += qry_row[3]; h100 += qry_row[6]
			long = qry_row[4] if qry_row[4] > long else long
	
	ttl_yds_per_rush = yds / rush
	ttl_yds_per_game = yds / num_gms	
	qry_table.add_row("Totals", "", str(rush), str(yds), f"{ttl_yds_per_rush:.1f}", f"{ttl_yds_per_game:.1f}", str(td), str(long), str(h100))
	console.print(qry_table)
	print()
	
# Individual Receiving

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Receiving")
	qry_table.add_column("Gms", justify="right")
	qry_table.add_column("Recept", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Rec", justify="right")
	qry_table.add_column("Yds/Gm", justify="right")
	qry_table.add_column("TD", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("Tgt", justify="right")
	qry_table.add_column("100+", justify="right")
	
	qry = """SELECT display_name, SUM(receptions) as ttl_recept, SUM(yards_receiving) AS yds, SUM(tds_receiving), MAX(long), SUM(targets), COUNT(*) as gms, COUNT(CASE WHEN yards_receiving > 99 THEN 1 END)
			FROM receiving
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY yds DESC, ttl_recept DESC"""
	qry_cursor.execute(qry, (abbr,))
	rec = yds = td = h100 = long = tgt = 0
	
	for qry_row in qry_cursor:
		if qry_row[1] > 0:
			yds_per_gm = qry_row[2] / qry_row[6]
			if qry_row[1] != 0:                     # In list if have tgt
				yds_per_rec = qry_row[2] / qry_row[1]
			else:
				yds_per_rec = 0
			qry_table.add_row(qry_row[0], str(qry_row[6]), str(qry_row[1]), str(qry_row[2]), f"{yds_per_rec:.1f}", f"{yds_per_gm:.1f}", str(qry_row[3]), str(qry_row[4]), str(qry_row[5]), str(qry_row[7]))
			rec += qry_row[1]; yds += qry_row[2]; td += qry_row[3]; tgt += qry_row[5]; h100 += qry_row[7]
			long = qry_row[4] if qry_row[4] > long else long
	
	ttl_yds_per_rec = yds / rec
	ttl_yds_per_game = yds / num_gms	
	qry_table.add_row("Totals", "", str(rec), str(yds), f"{ttl_yds_per_rec:.1f}", f"{ttl_yds_per_game:.1f}", str(td), str(long), str(tgt), str(h100))
	console.print(qry_table)
	print()

# Individual Fumbling

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Fumbling")
	qry_table.add_column("Fumbles", justify="right")
	qry_table.add_column("Fumbles Lost", justify="right")
	
	qry = """SELECT display_name, SUM(fumbles) AS ttl_fumb, SUM(fumbles_lost) AS ttl_fumb_lost
			FROM fumbles
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY ttl_fumb_lost DESC, ttl_fumb DESC"""
	qry_cursor.execute(qry, (abbr,))
	
	num_fumb = fumb_lost = 0
	for qry_row in qry_cursor:
		if qry_row[1] > 0:
			num_fumb += qry_row[1]
			fumb_lost += qry_row[2]
			qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]))

	if num_fumb == 0:
		print(" No Fumbles")
	else:
		qry_table.add_row("Totals", str(num_fumb), str(fumb_lost))
		console.print(qry_table)
	print()
	
# Kicking

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Kicking")
	qry_table.add_column("FG Made", justify="right")
	qry_table.add_column("FG Att", justify="right")
	qry_table.add_column("Pct", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("XP Made", justify="right")
	qry_table.add_column("XP Att", justify="right")
	qry_table.add_column("Pct", justify="right")
	
	qry = """SELECT display_name, SUM(fg_made) as fgm, SUM(fg_attempted) as fga, MAX(long), SUM(xp_made), SUM(xp_attempted)
			FROM kicking
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY fgm DESC, fga DESC"""
	qry_cursor.execute(qry, (abbr,))
	fgm = fga = long = xpm = xpa = 0
	
	for qry_row in qry_cursor:
		fgm += qry_row[1]; fga += qry_row[2]; xpm += qry_row[4]; xpa += qry_row[5]
		long = qry_row[3] if qry_row[3] > long else long
		fg_pct = qry_row[1] / qry_row[2] if qry_row[2] > 0 else 0
		xp_pct = qry_row[4] / qry_row[5] if qry_row[5] > 0 else 0
		qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]), f"{fg_pct:2.1%}", str(qry_row[3]), str(qry_row[4]), str(qry_row[5]), f"{xp_pct:2.1%}")
	
	ttl_fg_pct = fgm / fga
	ttl_xp_pct = xpm / xpa
	qry_table.add_row("Totals", str(fgm), str(fga), f"{ttl_fg_pct:2.1%}", str(long), str(xpm), str(xpa), f"{ttl_xp_pct:2.1%}")
	console.print(qry_table)
	print()
	
# Punting

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Punting")
	qry_table.add_column("Punts", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Punt", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("Touchbacks", justify="right")
	qry_table.add_column("Inside 20", justify="right")
	
	qry = """SELECT display_name, SUM(punts) as ttl_punts, SUM(yds) AS punt_yds, MAX(long), SUM(touchbacks), SUM(inside_20)
			FROM punting
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY punt_yds DESC, ttl_punts DESC"""
	qry_cursor.execute(qry, (abbr,))
	punt = yds = long = tchbk = ins20 = 0
	
	for qry_row in qry_cursor:
		punt += qry_row[1]; yds += qry_row[2]; tchbk += qry_row[4]; ins20 += qry_row[5]
		long = qry_row[3] if qry_row[3] > long else long
		yds_per_punt = qry_row[2] / qry_row[1] if qry_row[1] > 0 else 0
		qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]), f"{yds_per_punt:.1f}", str(qry_row[3]), str(qry_row[4]), str(qry_row[5]))
	
	ttl_yds_per_punt = yds / punt
	qry_table.add_row("Totals", str(punt), str(yds), f"{ttl_yds_per_punt:.1f}", str(long), str(tchbk), str(ins20))
	console.print(qry_table)
	print()
	
# Punt Returns

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Punt Returns")
	qry_table.add_column("Retns", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Retn", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("TD", justify="right")
	
	qry = """SELECT display_name, SUM(punt_returns) as ttl_retns, SUM(yds) AS retn_yds, MAX(long), SUM(punt_return_tds)
			FROM punt_returns
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY retn_yds DESC, ttl_retns DESC"""
	qry_cursor.execute(qry, (abbr,))
	
	num_retn = yds = td = long = 0
	for qry_row in qry_cursor:
		num_retn += qry_row[1]
		yds += qry_row[2]
		td += qry_row[4]
		long = qry_row[3] if qry_row[3] > long else long
		yds_per_retn = qry_row[2] / qry_row[1]
		qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]), f"{yds_per_retn:.1f}", str(qry_row[3]), str(qry_row[4]))
	
	if num_retn == 0:
		print(" No Punt Returns")
	else:
		yds_per_retn = yds / num_retn
		qry_table.add_row("Totals", str(num_retn), str(yds), f"{yds_per_retn:.1f}", str(long), str(td))
		console.print(qry_table)
	print()
	
# Kickoff Returns

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Kickoff Returns")
	qry_table.add_column("Retns", justify="right")
	qry_table.add_column("Yds", justify="right")
	qry_table.add_column("Yds/Retn", justify="right")
	qry_table.add_column("Long", justify="right")
	qry_table.add_column("TD", justify="right")
	
	qry = """SELECT display_name, SUM(kickoff_returns) as ttl_retns, SUM(yds) AS retn_yds, MAX(long), SUM(kick_return_tds)
			FROM kickoff_returns
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY retn_yds DESC, ttl_retns DESC"""
	qry_cursor.execute(qry, (abbr,))
	
	num_retn = yds = td = long = 0
	for qry_row in qry_cursor:
		num_retn += qry_row[1]
		yds += qry_row[2]
		td += qry_row[4]
		long = qry_row[3] if qry_row[3] > long else long
		yds_per_retn = qry_row[2] / qry_row[1]
		qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]), f"{yds_per_retn:.1f}", str(qry_row[3]), str(qry_row[4]))
	
	if num_retn == 0:
		print(" No Kickoff Returns")
	else:
		yds_per_retn = yds / num_retn
		qry_table.add_row("Totals", str(num_retn), str(yds), f"{yds_per_retn:.1f}", str(long), str(td))
		console.print(qry_table)
	print()
	
# Individual Defense
	
	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Individual Defense")
	qry_table.add_column("Gms", justify="right")
	qry_table.add_column("Tkls", justify="right")
	qry_table.add_column("Solos", justify="right")
	qry_table.add_column("Sacks", justify="right")
	qry_table.add_column("TFL", justify="right")
	qry_table.add_column("PD", justify="right")
	qry_table.add_column("QB Hit", justify="right")
	qry_table.add_column("TD", justify="right")
	
	qry = """SELECT display_name, SUM(tackles) as tkls, SUM(solo) as lone, SUM(sacks) AS sack, SUM(for_loss), SUM(passes_defensed), SUM(qb_hits), SUM(tds), COUNT(*) as gms
			FROM individual_defense
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY tkls DESC, lone DESC, sack DESC"""
	qry_cursor.execute(qry, (abbr,))
	tkl = solo = sks = tfl = pd = hit = td = 0
	
	for qry_row in qry_cursor:
		qry_table.add_row(qry_row[0], str(qry_row[8]), str(qry_row[1]), str(qry_row[2]), str(qry_row[3]), str(qry_row[4]), str(qry_row[5]), str(qry_row[6]), str(qry_row[7]))
		tkl += qry_row[1]; solo += qry_row[2]; sks += qry_row[3]; tfl += qry_row[4]; pd += qry_row[5]; hit += qry_row[6]; td += qry_row[7]
	
	qry_table.add_row("Totals", "", str(tkl), str(solo), str(sks), str(tfl), str(pd), str(hit), str(td))
	console.print(qry_table)
	print()
	
# Interceptions

	qry_table = Table(box=None, header_style="default")
	qry_table.add_column("Interceptions")
	qry_table.add_column("Int", justify="right")
	qry_table.add_column("Yds Returned", justify="right")
	qry_table.add_column("TD", justify="right")
	
	qry = """SELECT display_name, SUM(interceptions) as int, SUM(yds) AS int_yds, SUM(interception_tds)
			FROM interceptions
			WHERE team_abbr = ?
			GROUP BY player_id
			ORDER BY int DESC, int_yds DESC"""
	qry_cursor.execute(qry, (abbr,))
	
	num_int = yds = td = 0
	for qry_row in qry_cursor:
		num_int += qry_row[1]
		yds += qry_row[2]
		td += qry_row[3]
		qry_table.add_row(qry_row[0], str(qry_row[1]), str(qry_row[2]), str(qry_row[3]))
	
	if num_int == 0:
		print(" No Interceptions")
	else:
		qry_table.add_row("Totals", str(num_int), str(yds), str(td))
		console.print(qry_table)	
	print("--------------------------------------------------")
	print("\f")
	
# League Leaders

print("LEAGUE LEADERS")
print()

# Passing

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Passing Leaders")
qry_table.add_column("")
qry_table.add_column("Gms", justify="right")
qry_table.add_column("Comp", justify="right")
qry_table.add_column("Att", justify="right")
qry_table.add_column("Pct", justify="right")
qry_table.add_column("Yds", justify="right")
qry_table.add_column("Yds/Gm", justify="right")
qry_table.add_column("TD", justify="right")
qry_table.add_column("Int", justify="right")

qry = """SELECT display_name, SUM(completions) AS ttl_comp, SUM(attempts), SUM(yards_passing) AS yds, SUM(tds_passing) as tds, SUM(interceptions), COUNT(*) as gms, team_abbr
		FROM passing
		GROUP BY player_id
		ORDER BY yds DESC, tds DESC, ttl_comp DESC"""
qry_cursor.execute(qry)

for top_40 in range(1, 41):               #Python always has to go one past
	qry_row = qry_cursor.fetchone()
	yds_per_gm = qry_row[3] / qry_row[6]
	comp_pct = qry_row[1] / qry_row[2]
	qry_table.add_row(str(top_40), qry_row[0], qry_row[7], str(qry_row[6]), str(qry_row[1]), str(qry_row[2]), f"{comp_pct:2.1%}", str(qry_row[3]), f"{yds_per_gm:.1f}", str(qry_row[4]), str(qry_row[5]))
	
console.print(qry_table)
print("\f")

# Rushing

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Rushing Leaders")
qry_table.add_column("")
qry_table.add_column("Gms", justify="right")
qry_table.add_column("Carries", justify="right")
qry_table.add_column("Yds", justify="right")
qry_table.add_column("Yds/Rush", justify="right")
qry_table.add_column("Yds/Gm", justify="right")
qry_table.add_column("TD", justify="right")
qry_table.add_column("Long", justify="right")

qry = """SELECT display_name as Name, 
		team_abbr as Team, 
		SUM(rushes) as Rushes, 
		SUM(yards_rushing) as TotalYards, 
		SUM(tds_rushing) as TDs,
		MAX(long) as Long,
		COUNT(*) as gms
		FROM rushing
		GROUP BY display_name
		ORDER BY TotalYards DESC, Rushes DESC, TDs DESC"""
qry_cursor.execute(qry)

for top_40 in range(1, 41):
	qry_row = qry_cursor.fetchone()
	yds_per_gm = qry_row[3] / qry_row[6]
	yds_per_rush = qry_row[3] / qry_row[2]
	qry_table.add_row(str(top_40), qry_row[0], qry_row[1], str(qry_row[6]), str(qry_row[2]), str(qry_row[3]), f"{yds_per_rush:.1f}", f"{yds_per_gm:.1f}", str(qry_row[4]), str(qry_row[5]))
	
console.print(qry_table)
print("\f")

# Receiving

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Receiving Leaders")
qry_table.add_column("")
qry_table.add_column("Gms", justify="right")
qry_table.add_column("Recepts", justify="right")
qry_table.add_column("Yds", justify="right")
qry_table.add_column("Yds/Recept", justify="right")
qry_table.add_column("Yds/Gm", justify="right")
qry_table.add_column("TD", justify="right")
qry_table.add_column("Long", justify="right")

qry = """SELECT display_name as Name, 
		team_abbr as Team, 
		SUM(receptions) as Recepts, 
		SUM(yards_receiving) as TotalYards, 
		SUM(tds_receiving) as TDs,
		MAX(long) as Long,
		COUNT(*) as gms
		FROM receiving
		GROUP BY display_name
		ORDER BY TotalYards DESC, Recepts DESC, TDs DESC"""
qry_cursor.execute(qry)

for top_60 in range(1, 61):               #Python always has to go one past
	qry_row = qry_cursor.fetchone()
	yds_per_gm = qry_row[3] / qry_row[6]
	yds_per_recept = qry_row[3] / qry_row[2]
	qry_table.add_row(str(top_60), qry_row[0], qry_row[1], str(qry_row[6]), str(qry_row[2]), str(qry_row[3]), f"{yds_per_recept:.1f}", f"{yds_per_gm:.1f}", str(qry_row[4]), str(qry_row[5]))
	
console.print(qry_table)
print("\f")

# Defense Leaders

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Defensive Leaders by Tackles")
qry_table.add_column("")
qry_table.add_column("Gms", justify="right")
qry_table.add_column("Tkls", justify="right")
qry_table.add_column("Solos", justify="right")
qry_table.add_column("Sacks", justify="right")
qry_table.add_column("TFL", justify="right")
qry_table.add_column("PD", justify="right")
qry_table.add_column("QB Hit", justify="right")
qry_table.add_column("TD", justify="right")
	
qry = """SELECT display_name, SUM(tackles) as tkls, SUM(solo) as lone, SUM(sacks) AS sack, SUM(for_loss), SUM(passes_defensed), SUM(qb_hits), SUM(tds), COUNT(*) as gms, team_abbr
		FROM individual_defense
		GROUP BY player_id
		ORDER BY tkls DESC, sack DESC"""
qry_cursor.execute(qry)
	
for top_40 in range(1, 41):
	qry_row = qry_cursor.fetchone()
	qry_table.add_row(str(top_40), qry_row[0], qry_row[9], str(qry_row[8]), str(qry_row[1]), str(qry_row[2]), str(qry_row[3]), str(qry_row[4]), str(qry_row[5]), str(qry_row[6]), str(qry_row[7]))
	
console.print(qry_table)
print()

# Defense Leaders by Sack

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Defensive Leaders by Sack")
qry_table.add_column("")
qry_table.add_column("Gms", justify="right")
qry_table.add_column("Tkls", justify="right")
qry_table.add_column("Solos", justify="right")
qry_table.add_column("Sacks", justify="right")
qry_table.add_column("TFL", justify="right")
qry_table.add_column("PD", justify="right")
qry_table.add_column("QB Hit", justify="right")
qry_table.add_column("TD", justify="right")
	
qry = """SELECT display_name, SUM(tackles) as tkls, SUM(solo) as lone, SUM(sacks) AS sack, SUM(for_loss), SUM(passes_defensed), SUM(qb_hits), SUM(tds), COUNT(*) as gms, team_abbr
		FROM individual_defense
		GROUP BY player_id
		ORDER BY sack DESC, tkls DESC"""
qry_cursor.execute(qry)
	
for top_40 in range(1, 41):
	qry_row = qry_cursor.fetchone()
	qry_table.add_row(str(top_40), qry_row[0], qry_row[9], str(qry_row[8]), str(qry_row[1]), str(qry_row[2]), str(qry_row[3]), str(qry_row[4]), str(qry_row[5]), str(qry_row[6]), str(qry_row[7]))
	
console.print(qry_table)
print()

# Interceptions

qry_table = Table(box=None, header_style="default")
qry_table.add_column("", justify="right")
qry_table.add_column("Interceptions")
qry_table.add_column("")
qry_table.add_column("Int", justify="right")
qry_table.add_column("Retn Yds", justify="right")
qry_table.add_column("TD", justify="right")
	
qry = """SELECT display_name, team_abbr, SUM(interceptions) as int, SUM(yds) AS int_yds, SUM(interception_tds)
		FROM interceptions
		GROUP BY player_id
		ORDER BY int DESC, int_yds DESC"""
qry_cursor.execute(qry)
	
for top_10 in range(1, 11):
	qry_row = qry_cursor.fetchone()
	qry_table.add_row(str(top_10), qry_row[0], qry_row[1], str(qry_row[2]), str(qry_row[3]), str(qry_row[4]))
	
console.print(qry_table)

db_conn.close()