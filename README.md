# ESPN-API
*MLB Box Scores Updated for ESPN API updates for 2025 season.*

Miscellaneous Python Linux command line utilities to access the ESPN API. Primarily designed for post-game box scores, but they can be used for game preview data as available, and in-game partial box scores.

Libraries now in use, as of 6-17-2024:  
* urllib  
* json  
* sys  
* datetime  
* pytz  
* re  
* rich  

Most of these are included in most standard Python installs, however, double check & install if necessary. Rich will likely need to be installed in most cases, so use "pip install rich" on the regular command line (see https://pypi.org/project/rich/). If nagged about forced, unncessary "external management", use "sudo apt install python3-rich" (generally, sudo apt install python3-{package-name}).

Use python3 -u to help reduce API caching; download .py file to your computer & use python3 to run:

Example Usage: python3 -u ESPNNFLAPIBoxScores.py YYYYMMDD

Date parameter is optional to select a specific date for the games. Due to API throttling, only 1 date is accepted (script if you require more, however, some utilities accept a date range, but that use is not recommended).

This project is posted under the GNU General Public License v3.0. If you intend to sell a product based on this code, or release a modified version of this code to the public, that code must also carry this license & be released to the public as open source.
