# Extraction of Sports Particulars as Networks (ESPN)
<p align="center">
	<img src="images/logo.png" alt="logo" width="600"/>
</p>


**ESPN** is the first ever transformation tool to convert sports data in tabular or unstrucuted format into a network style format like `.gml`. As well as collecting sports data as networks, you only need to provide what you want and **ESPN** will do the rest.

---

### Problem
When using network data formats like `.gml` or a `.csv` that explicitly states what the source and target nodes are, there is no room for customization and variability. Often times, finding the right network data is hard, time consuming, and sometimes impossible. This is where **ESPN** comes into play.

### Solution
**ESPN** allows for users to completely customize their querying experience for extracting any sports information at the player or team level. Want to establish a network of MLB players from the 1971 season to see how players interactions led the Pirates to a World Series? You can! Want to analyze all NFL team games in the 21st century for studying effects of losses or wins? Great! You can do that to. The possibilities are endless!

### Currently Supports
| :white_check_mark: NFL <img width=200/> | :x: MLB <img width=200/> | :x: NHL <img width=200/> | :x: NCAAF <img width=200/> | :x: NCAAB <img width=200/> |
| --- | --- | --- | --- | --- |

---

# Sample Response
Say you would like to query the 1980 NFL season for all games at the team level. The search query url will be `https://extractsportsparts.network/?sport=nfl&year=1980&week=all&team=all&player=all&level=team&postseason=false`. The response would be as follows:
```gml
graph[
	multigraph 1
	node[
	 id "Buffalo Bills"
	 label "Bills"
	 location "Buffalo"
	]
	node[
	 id "Miami Dolphins"
	 label "Dolphins"
	 location "Miami"
	]
	...
	edge[
	 source "Miami Dolphins"
	 target "Buffalo Bills"
	 source_score 7
	 target_score 17
	 week 1
	 year 1980
	 is_postseason "False"
	]
	edge[
	 source "Tampa Bay Buccaneers"
	 target "Cincinnati Bengals"
	 source_score 17
	 target_score 12
	 week 1
	 year 1980
	 is_postseason "False"
	]
    ...
]
```
and the network will look as follows
<p align="center">
  <img width="600" height="400" src="images/example.png">
</p>

### Time for response
The following displays the estimated times of how fast the data is queried and responded

| (/week/year) 	| NFL   	| MLB 	| NHL 	| NCAAF 	| NCAAB 	|
|--------------	|-------	|-----	|-----	|-------	|-------	|
| Team         	| 5.83s 	|     	|     	|       	|       	|
| Player       	| 5.89s 	|     	|     	|       	|       	|
