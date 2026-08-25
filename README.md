# ESPN-API

Miscellaneous Python command line utilities to access the ESPN API. Primarily designed for post-game box scores, but they can be used for game preview data as available, and in-game partial box scores. Includes utilities for maintaining a NFL SQLite database throughout the season.

**Note that there are [updates for the upcoming NFL season](#new-nfl-updates-for-august-2026), as well as a brand new system for [downloading a daily soccer final score roundup](#soccer-final-score-daily-roundup-instructions).**

## Basic Instructions for box score scripts (read [update section](#new-nfl-updates-for-august-2026) before use)

Download .py file to your computer & use python3 to run. Note that you must have the Rich Python library installed ([read special note](#rich-library-note)). Example usage:

`python3 -u ESPNNFLAPIBoxScores.py YYYYMMDD`  

Use python3 -u to help reduce API caching. Date parameter is optional, but the API revolves around date-based queries. If no date is specified prior to around 10 AM US Eastern time, games from the previous day are supplied. After that time, the current day's games are returned.

To specify a day, most scripts require that only one date may be used per run, in order to reduce API data throttling. Some scripts allow for a date range, or use a shell script to get box scores for multiple days. Use the redirection operator (>) in the command to save box scores to a file.

This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.

## New NFL Updates for August 2026

The NFL box scores, SQLite database load, and reports have some additions.  

* The addition of a parameter to specify the name of the SQLite database to be loaded to or reported from in the command line. .db or .sqlite can be used for the database file extension. When creating a new database, use a new file name, as the creation process destroys data. Use the following command line formats:

`python3 CreateNFLStatsSqliteDB.py new_database_file_name.sqlite`  
`python3 -u ESPNNFLAPISqlite.py YYYYMMDD database_file_name.sqlite` using one game day as a parameter and the database must already exist  
`python3 ESPNNFLAPISqliteReport.py database_file_name.sqlite`  
`python3 ESPNNFLAPISqliteIndividualStatsReport.py database_file_name.sqlite`

* For full instructions, see the [NFL database utilities section below.](#nfl-database-utilities)
* The addition of fumble recoveries and forced fumbles to the *defensive players' statistics only*. Please note that fumble stats are unusual and that I have not added stats for bad snaps, a player just dropping the ball on his own, or for the offense just falling on their own fumbles. Totals appear on box scores and are included in the SQLite database load & in the two report scripts. Fumbles on returns should appear in its normal place on the box score & in the fumbles table.  
* The addition of the scoring_plays table, including a description with scoring player's name, yardage, play type, and conversion if a touchdown. Missed field goals also have a row in the table, described as such. Columns:

`team_abbr - game_date - opponent_abbr - home_visitor - play_descr - qtr - play_time`  

* Missed field goals have also been added to the box score.
* Reception percentages have been added to the main report script.
* Also added to the end of the main report script are the team ranking tables for the following aggregate statistics: Offensive & Defensive Points per Game, Offensive & Defensive Total Yards per Game, Offensive & Defensive Rushing Yards per Game, and Offensive & Defensive Passing Yards per Game.

## Soccer Final Score Daily Roundup Instructions

The soccer API scoreboard call has a nice summary of stats, when available (otherwise just shows as 0's), a game summary, including goal scorers & card recipients, league name, date, stadium, and any available brief game write-up. The script (ESPNAPISoccerFinals.py) has been made flexible in order to accomodate only the leagues that you might be interested in.

First, check out the following URL, preferably in Firefox which has a built in JSON "pretty print" facility, or use a JSON Pretty Print utility of your own:

`https://site.api.espn.com/apis/site/v2/leagues/dropdown?sport=soccer`

There is only one first level index in the JSON that loads, "leagues". Under that level are the 218 leagues available in the soccer API, as of August 2026. Open the 'leagues' as required by the pretty print utility (in Firefox, click the twisty arrow and the twisty arrow for the grouping of 100 entries). Then, open the '0' index, and you'll see its name, "FIFA World Cup". Most importantly, notice the "slug" key value, "fifa.world". This slug is used to tell the API the league for which you want scores, using the following URL format:

`http://site.api.espn.com/apis/site/v2/sports/soccer/slug/scoreboard`

In this case:

`http://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard`

Add that URL to a text file, if desired. Add any other leagues that you are interested in to that text file. I have uploaded a sample text file that I use for European soccer leagues, EuropeanSoccerSlugList.txt, to provide an example. Then, for the daily roundup of final scores from your listed leagues, using a single date specified in YYYYMMDD format, use the command:

`python3 ESPNAPISoccerFinals.py YYYYMMDD your_slug_url_file.txt`

As usual, redirect the output to a file if you wish, and be sure to specify any paths if any files are in a different directory.

## NFL database utilities

1. To set up your own local copy of the SQLite database, run `python3 CreateNFLStatsSqliteDB.py new_database_file_name.sqlite`.
2. Updates need to be made daily, game date being specified in YYYYMMDD format,  `python3 -u ESPNNFLAPISqlite.py YYYYMMDD database_file_name.sqlite`.
3. Use a SQLite tool (my favorite is DB Browser for SQLite) to access the data and view the schema. For example, to view the rushing season totals for carries, total yards, and total touchdowns, grouped by runner, & sorted descending by yards:

```
SELECT display_name as Name, 
team_abbr as Team, 
SUM(rushes) as Rushes, 
SUM(yards_rushing) as TotalYards, 
SUM(tds_rushing) as TDs,
MAX(long) as Long
FROM rushing
GROUP BY display_name
ORDER BY TotalYards DESC;
```

Two text-based reports are also available, ESPNNFLAPISqliteReport & ESPNNFLAPISqliteIndividualStatsReport. To run, download the Python scripts, and use  [the last two command lines specified above](#new-nfl-updates-for-august-2026). The Sqlite Report contains full team & player stats, by team, league leaders, and team rankings. The Individual Stats report, has by-game box scores for each individual player on every team, so it is much longer. Note that page break characters are included, so they format nicely in a word processing program. Check the [special notes](#football-database-notes) for further information.

### Rich library note

Most of the Python libraries are included in most standard Python installs, however, double check & install if necessary. Rich will likely need to be installed in most cases, so use `pip install rich` on the regular command line ([Rich site](https://pypi.org/project/rich/)). If nagged about forced, unnecessary "external management", use `sudo apt install python3-rich` (generally, `sudo apt install python3-{package-name}`).

### Football Database Notes

* ESPN commits a lot of database changes for the new week on Tuesday late afternoons, Eastern US Time, making access unavailable.
* The College Football box scores are set up for games involving FBS teams only. The API, in general, is quite incomplete for regular-season games where both teams are in the FCS.
* The database load script (ESPNNFLAPISqlite.py) simply overwrites previously loaded games, should a game's statistics be loaded twice.
* Passing yards in the team totals section are "net", which subtracts sack yardage; player totals do not subtract sacks.
* If a player is traded, that player's statistics will reported showing the stats earned for each team.
