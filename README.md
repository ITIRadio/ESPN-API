# ESPN-API
### World Cup box scores now available.

Usage: python3 ESPNWorldCupSoccerAPIBoxScores.py YYYYMMDD YYYYMMDD

Due to fewer games being held per day and thus fewer API calls being required, two date parameters are allowed, earliest date first (otherwise will return no games). One date parm receives games from that day (US Eastern time), and no parms returns today's games. Previews for future games & summaries of games in progress also included.

Miscellaneous Python Linux command line utilities to access the ESPN API. Primarily designed for post-game box scores, but they can be used for game preview data as available, and in-game partial box scores. Includes utilities for maintaining a NFL SQLite database throughout the season.

### *About the NFL SQLite database utilities:*

1. To set up your own local copy of the SQLite database, run `python3 CreateNFLStatsSqliteDB.py` (with script in desired database directory).
2. Updates need to be made daily, run `python3 -u ESPNNFLAPISqlite.py YYYYMMDD` (date in YYYYMMDD format, with script & database in desired directory). Doing updates the next day after a game day works best.
3. Use a SQLite tool (my favorite is DB Browser for SQLite) to access the data and view the schema. There are no foreign keys in the database, as, at least for my application, I'm just doing queries against one table at a time. For example, to view the rushing season totals for carries, total yards, and total touchdowns, grouped by runner, & sorted descending by yards:

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
4. A new report, using rich text tables, has also been uploaded. It contains a statistical report for each team, and league leaders tables. Page breaks are included, so redirecting to a text file, and opening the text file in a word processing program, will automatically include page breaks. This will come in handy, as the report is already 84 pages long, as of September 19. There is also another new report for each player with statistics by game; note that this report is much longer. Also note that if a player changes teams, that player's statistics will be listed in two separate places, one under each team. *Update 12-5-25:* new totals have been provided by each position group of players by team, new totals for points for & points against, and a second list of defensive leaders sorted by sack. Note that passing yards in the team totals section is "net", as in shown after subtracting sack yardage; player totals do not subtract sacks.
5. Be aware though, that ESPN is changing the database over for the new week on Tuesday late afternoons, Eastern US Time. During that time, some box scores become temporarily unavailable, and will thus kick out errors. Time your database updates accordingly. The software simply overwrites previously loaded box scores, should a game's statistics be loaded twice.

*Note about required library install for rich:* Most of the Python libraries are included in most standard Python installs, however, double check & install if necessary. Rich will likely need to be installed in most cases, so use "pip install rich" on the regular command line (see https://pypi.org/project/rich/). If nagged about forced, unncessary "external management", use "sudo apt install python3-rich" (generally, sudo apt install python3-{package-name}).

Use python3 -u to help reduce API caching; download .py file to your computer & use python3 to run:

Example Usage: python3 -u ESPNNFLAPIBoxScores.py YYYYMMDD

Date parameter is optional to select a specific date for the games. Due to API throttling, only 1 date is accepted (script if you require more, however, some utilities accept a date range, but that use is not recommended).
This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.
