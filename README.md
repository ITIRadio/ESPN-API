# ESPN-API
### *NFL & CFB now updated for 2025 season, plus new utilities for maintaining NFL SQLite database throughout the season.*

Miscellaneous Python Linux command line utilities to access the ESPN API. Primarily designed for post-game box scores, but they can be used for game preview data as available, and in-game partial box scores.

### *About the new NFL SQLite database utilities:*

1. To set up your own local copy of the SQLite database, run python3 CreateNFLStatsSqliteDB.py (with script in desired database directory).
2. Updates need to be made daily, run python3 -u ESPNNFLAPISqlite.py YYYYMMDD (date in YYYYMMDD format, with script & database in desired directory). Doing updates the next day after a game day works best.
3. Use a SQLite tool (my favorite is DB Browser for SQLite) to access the data and view the schema. There are no foreign keys in the database, as, at least for my application, I'm just doing queries against one table at a time. For example, to view the rushing season totals for carries, total yards, and total touchdowns, grouped by runner, & sorted descending by yards:

```
SELECT display_name as Name, 
team_abbr as Team, 
SUM(rushes) as Rushes, 
SUM(yards_rushing) as TotalYards, 
SUM(tds_rushing) as TDs
FROM rushing
GROUP BY display_name
ORDER BY TotalYards DESC;
```

### Other news:
* Some new fields have been added to the NFL API for this season; those have been included in the box score. Also, previews (run on a given date prior to the games) have been upgraded (abbreviated in-game box scores have been kept).
* The CFB API is pretty much the same, and some issues, like timeouts never updating during games, still remain.
* Some games involving FCS teams are *NOT* being updated live anymore, or have significant amounts of stats missing. Rather, ESPN is waiting for post-game reports to then load to their database. Such games seem to be available by the next day. You can use the current CFB script for FCS games by changing the two url variable assignments in the Mainline to "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=81&limit=200&dates=" and "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=81&limit=200" (group 80 is all FBS & FBS vs. FCS games, group 81 is all FCS games).

*Note about required library install for rich:* Most of the Python libraries are included in most standard Python installs, however, double check & install if necessary. Rich will likely need to be installed in most cases, so use "pip install rich" on the regular command line (see https://pypi.org/project/rich/). If nagged about forced, unncessary "external management", use "sudo apt install python3-rich" (generally, sudo apt install python3-{package-name}).

Use python3 -u to help reduce API caching; download .py file to your computer & use python3 to run:

Example Usage: python3 -u ESPNNFLAPIBoxScores.py YYYYMMDD

Date parameter is optional to select a specific date for the games. Due to API throttling, only 1 date is accepted (script if you require more, however, some utilities accept a date range, but that use is not recommended).

This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.
