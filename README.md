# nba-hackathon

An analysis of defender impact on a player's effectiveness throughout the course of a game.
<br><br>
[Pranav Badami](https://github.com/pranavbadami) • [Charlie DiGiovanna](https://github.com/cd17822) • [Sean Viswanathan](https://github.com/SeanViswanathan)
<br><br>
Using Pandas on a Python Flask server, we were able to parse SportVU and Play-by-Play data to analyze how a player's efficiency fluctuates based on his defender throughout the course of a game. With D3, we illustrated the defender by minute using colored bands in order to visualize his impact on the player's efficiency. See a snippet of the app in action below:
<br><br>
<img src="http://i.freegifmaker.me/1/4/7/5/0/2/14750291532416655.gif?1475029167" alt="gifs website"/>
<br><br>
To identify a player's defender, we analyzed raw SportVU data which gives us court positions for all players and the ball at 25 FPS resolution. We calculate player distances for defenders relative to the offensive player for every frame, and group by seconds and then minutes. On aggregated group level data, we appoint the most frequent closest defender as the offensive player's primary defender; this allows our D3 frontend to render colored bands based on defender for stretches in the game.
