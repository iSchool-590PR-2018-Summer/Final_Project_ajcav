# Fantasy Football Lineup Optimization with Monte Carlo Simulation

## Alex Cavanaugh

# Monte Carlo Simulation Scenario & Purpose:
This program uses a Monte Carlo simulation to create a distribution for player statistics that are relevant to fantasy
football. This information is then organized and presented to the user as a lineup of players that are likely to earn
the most points in a season. This program can also be used in a live draft to dynamically create the optimal team given that not all players are available. 

## Simulation's variables of uncertainty:
The variables of uncertainty here are the methods that players can earn points. For example, throwing a touchdown pass,
making an interception, blocking a field goal, etc. In the simulation, a random year and week are selected (with more
recent years having a higher probability of being chosen), and the players points in a certain stat during that random
year/week give the value for the variable. I chose to weigh more recent years more heavily since a players performance
is likely a slow-changing variable. 

## Hypothesis or hypotheses before running the simulation:
I think this program may skew towards picking groups of players that generally have big plays together, such as a QB and
WR. However, this may not be the best strategy in fantasy football since you're putting all your eggs in one basket. At the same time, more risk means more reward. Your milage may vary. 

## Analytical Summary of findings:
It was surprising that the team stacking was not as extreme as I had imaged. There seems to be a healthy distribution of players across various teams and positions. While I did begin to see convergence as I increased the number of simulations per player to 100, there may be even more room to test this. Unfortunately, running these tests take a long time, and tests must be run for every active player which compounds this issue. One possible solution would be to remove players that the user thinks will perform poorly and not simualte those players at all, or to eliminate the bottom percentile of players with each successive iteration.

## Instructions on how to use the program:
The first thing to mention about this program, is that due to unmaintained libraries, you **must use Python 2.7**. I've tested this program using Python 2.7.11. 

There are two ways to use this program. The first would be to simply generate an optimal lineup for this NFL season using information from the previous seasons. Using this method, the user can choose the number of Monte Carlo simulatios to run, as well as include/exclude players from their optimal roster. One thing to note is that using the program in this way is extremely time consuming for a large number of MC simulations since the simulations are run on every player. If you just want to view an optimal team, you can find it in the `100_sim_optimal_team` file. This file was generated as the result of 100 MC simulations. 

Another way to use this program is to use the results of the MC simulation for a draft. The `live_draft.py` script enables a user to have a live draft, and the optimal team is generated on the fly. The user will be asked to enter in the picks of other members of their league, as well as their own picks. However, before the users turn to pick, they will be shown the *best possible roster at that point in time*. This means that players that other league members have picked will have been removed and substituted with the next highest scoring player that can fill the same role (this may not always be the same position). 

Regardless of how you choose to use the program, the following packages are required: 
1. pandas 
2. tabulate
3. nflgame
4. numpy

These can all be installed via pip. `pip install <package_name>`

### Creating an Optimal Team
In order to generate the optimal team, we query stats for individual players. These stats are obtained via the nflgame library. There are a few steps before we can import nflgame into our python project and get all the information we would expect to find. First, a small change must be made in the `update_players.py` file. This will most likely be found in a path similar to `C:\Python27\Lib\site-packages\nflgame\update_players.py`. With this file open, change line 179 from

`last_name, first_name = map(lambda s: s.strip(), name.split(','))`

to

`last_name, first_name = map(lambda s: s.strip(), name.split(',')[:2])`

Now we're ready to run the `update_players.py` script which will pull an updated list of players from the 2017 season. Run `python update_players.py` and you should see some output indicating that the script is looking for players. It may take a while to download all the information. Also, you may get some errors while running this. When I ran the script, I ultimately had 75 players that the script could not gather information on. These players did not have enough information to be used in the simulation, so we can ignore these errors.


Next, we need to update the game schedule. To do this, run `python update_sched.py --year 2017`. (The `update_sched.py` file should be in the same location at the `update_players.py` file.)

Finally, we should be ready to use the `lineup_optimizer.py` script in this program. When you run the script, the program will ask for any players that you would like to include on your team regardless of their MC score, and any players that should be excluded from your team (regardless of MC score). Next, the program will ask for the number of MC simulations to be performed. Finally, the program will perform the required simulations, and display the optimal roster to the user. A small number of simulations (<10) should run relatively quickly, however as the number of simulations grows, the time to execute grows significantly. 

### Live Drafting
To use this program in a live draft, use the `live_draft.py` script. When running the script, the user will first be asked to enter the name of the file with all player information. This can be obtained by running the `lineup_optimizer.py` script, or you can use the provided file. If using the provided information file, the filename should be `100_sim_all_players`. Next, the user will continuously be asked to enter in the picks of the other members of their league. When it is the users turn to pick, they will be shown an optimal roster and should pick from that list for the best results (though it isn't necessary). Once the user has picked a full team, the program quits. It should also be mentioned that this program will not allow the user to pick an illegal team - so if a player is chosen and added to the roster, it is guaranteed that a legal roster can still be created. 

## All Sources Used:
nflgame documentation: http://web.archive.org/web/20171205024904/http://pdoc.burntsushi.net:80/nflgame#nflgame.one
