import nflgame
import numpy as np
import pandas as pd
from tabulate import tabulate


def validate_player(player):
    """
    This method takes in a string (player) which is the name of a player that the user is trying to find. The method
    then searches for the player. If the search yields more than one result, the user will be prompted to select which
    player they would were intending.

    :param player: string, name of player the user is searching for
    :return: Player object that the user has selected
    """

    # Search for the player, record all matches
    matches = nflgame.find(player)

    # If we only found one result, return it
    if len(matches) == 1:
        return matches[0]

    # If we didn't find anything, return nothing
    elif len(matches) == 0:
        return None

    # If we made it this far, we found more than one match
    print('Found '+str(len(matches))+' matches for '+player.title()+'.')
    print('Please select from the following options.')

    # List the matches that were found in the search
    for i in range(len(matches)):
        print('('+str(i+1)+') - '+player.title()+', '+matches[i].team+', number '+str(matches[i].number))

    # Prompt the user to select which player they were looking for
    selection = int(raw_input('Enter your selection: '))
    return matches[selection-1]


def get_active_players():
    """
    This method does not take any inputs. It searches the list of players in the nflgames.players variable, and returns
    a list of players marked as active (player.status == 'ACT').

    :return: list of active Players
    """

    # Get a list of all nfl players in the database
    all_players = nflgame.players

    # Initialize empty list for active players
    available_players = []

    # Go through all players
    for p in all_players:

        # If the players are active, they are available for our roster
        if all_players[p].status == 'ACT':
            available_players.append(all_players[p])

    # Return all players that are available
    return available_players

def score_to_fantasy_points(player):
    """
    This method converts the plays made by a player into fantasy football points.

    :param player: Player object (with combined plays)
    :return: float, points earned by the Player
    """

    point_conversion = {'passing_twoptm': lambda x: x*2.0,
                        'passing_yds': lambda x: x/5.0*0.2,
                        'passing_tds': lambda x: x*4.0,
                        'passing_ints': lambda x: x*(-2.0),
                        'rushing_yds': lambda x: x*0.1,
                        'rushing_tds': lambda x: x*6.0,
                        'rushing_twoptm': lambda x: x*2.0,
                        'receiving_yds': lambda x: x*0.1,
                        'receiving_rec': lambda x: x*0.5,
                        'receiving_tds': lambda x: x*6.0,
                        'receiving_twoptm': lambda x: x*2.0,
                        'kickret_tds': lambda x: x*6.0,
                        'puntret_tds': lambda x: x*6.0,
                        'fumbles_lost': lambda x: x*(-2.0),
                        'kicking_fgb': lambda x: x*(-1.0),
                        'fumbles_rec_tds': lambda x: x*6.0,
                        'defense_int_tds': lambda x: x*6.0,
                        'fumble_rec_tds': lambda x: x*6.0,
                        'defense_safe': lambda x: x*2.0,
                        'defense_fgblk': lambda x: x*2.0,
                        'defense_puntblk': lambda x: x*2.0,
                        'defense_int': lambda x: x*2.0,
                        'fumbles_rec': lambda x: x*2.0,
                        'kicking_fgmissed': lambda x: x*(-1.0),
                        'defense_sk': lambda x: x*1.0}

    # Initialize points to zero
    points = 0.0

    # Go through each stat (or play) in the player
    for stat in player._stats:

        # If the play can be mapped to fantasy football points...
        if stat in point_conversion.keys():

            # Add the number of points earned to the total points
            points += point_conversion[stat](getattr(player, stat))

    return points


def get_player_score(player):
    """
    This method takes in a Player object. A random week/year is selected, and the players fantasy football points for
    that week/year are queried and returned.

    :param player: Player to calculate points for
    :return: float, number of points earned by Player
    """

    # Only loop through a finite number of times to find games that a user has played in.
    i = 0
    while i < 8:
        i += 1

        # Get random week/year to query
        year = np.random.choice([2014, 2015, 2016, 2017], p=[0.1, .15, .25, .5])
        week = np.random.randint(1, 18)

        # Combine all plays from all games during this time period
        games = nflgame.games(year, week=week)
        games = nflgame.combine_game_stats(games)

        # Go through each person involved in the plays
        for person in games:

            # If the player is blank, move to the next
            if person.player is None:
                continue

            # If the player is the desired player, convert plays to fantasy points
            if player == person.player:
                return score_to_fantasy_points(person)

    # If we can't find any games that this player has played in, they probably aren't a good pick for the team (since
    # they don't play frequently), so return -inf so that they aren't selected in the optimization.
    return -float('Inf')


def simulate(team, N=100):
    """
    This function runs a Monte Carlo simulation by selecting a random year (weighted heuristically since more recent
    years are a better reflection of player ability) and random week to sample a players fantasy score. The average
    score for a player is averaged over N simulations, then added to the team score. The total team score is returned.

    :param team: list of Player objects
    :param N: number of simulations to run
    :return: total points for team
    """

    # Initialize total score for team
    total_score = 0.0

    # Go through each player on the team
    for player in team:
        simulation_score = []

        # Simulate their score N times
        for i in range(N):
            simulation_score.append(get_player_score(player))

        # Add the average of the N simulations to the total team score
        if len(simulation_score) != 0:
            total_score += np.mean(simulation_score)
    return total_score


def players_to_df(players, N):
    """
    This method takes in a list of Players and puts this information into a pandas df. It also calls the function to
    run the MC simulation on each player so that the information is available in the df.

    :param players: list of Player objects to be included in the df
    :param N: int number of times to run the MC simulation on each player
    :return: pandas dataframe with information on each Player
    """

    # Initialize empty dataframe
    df = pd.DataFrame(columns=['full_name','team','position','points','player_object'])

    # Go through each Player in the list of players, and add their information to the dataframe
    for index, p in enumerate(players):
        if N != 0:
            print('Simulating player '+str(index+1)+' of '+str(len(players)))
        df.loc[p.player_id] = [p.full_name, p.team, p.position, simulate([p], N), p]
    return df


def football_pos_to_ff_pos(position):
    """
    This method takes in a string representation of a football position, and maps it to groups that are used to regulate
    the number of each player type on a fantasy team.

    :param position: string, player position (e.g. 'QB' or 'WR')
    :return: string, group for fantasy football (e.g. 'QB' --> 'QB', 'DT' --> 'D/ST')
    """

    if position == 'QB':
        return 'QB'
    elif position == 'RB':
        return 'RB'
    elif position == 'WR':
        return 'WR'
    elif position == 'TE':
        return 'TE'
    elif position == 'K':
        return 'K'
    elif position in ['DB','DE','DT','CB','LS','LB','P','ILB','OLB','T','NT']:
        return 'D/ST'

    # If the position is not in the list, return None
    return None


def can_add_player(roster, new_position):
    """
    This method takes in the current roster, and the position of a new player that the program is trying to add to the
    roster. Essentially, this method looks at the rules about how a fantasy football team can be arranged, and ensures
    that these rules are still satisfied if the new player is added.

    :param roster: pandas DataFrame containing the current team
    :param new_position: string, position of player to be added to team
    :return: boolean, indicating whether or not this player can be legally added to the roster
    """

    # If the position is blank, or not in the list of fantasy positions, we cannot add the player to the roster
    if new_position == '' or not football_pos_to_ff_pos(new_position):
        return False

    # If we already have a full roster, we can't add another player
    if len(roster.index) >= 16:
        return False

    # This is the [min,max] number of players that can be in each position group.
    team_restrictions = {'QB': [1,4],
                         'RB': [2,8],
                         'WR': [2,8],
                         'TE': [1,3],
                         'K': [1,3],
                         'D/ST': [1,3]}

    # Indicates if we have used our flex spot yet (flex can be WR, RB, or TE)
    flex_used = False

    # Go through each row in the roster, and subtract the positions of the players on the roster from the
    # team_restrictions (unless the player qualifies as flex (this can be used only once)).
    for index, row in roster.iterrows():
        if football_pos_to_ff_pos(row['position']):
            if row['position'] in ['TE','RB','WR'] and not flex_used:
                flex_used = True
                continue

            pos = football_pos_to_ff_pos(row['position'])
            team_restrictions[pos] -= np.ones(2)

    # Simulate the new position being added to the roster
    team_restrictions[football_pos_to_ff_pos(new_position)] -= np.ones(2)

    # If we've surpassed the maximum number of players allowed in one position group, v[1] will be negative, indicating
    # that we cannot legally add this player
    for v in team_restrictions.values():
        if v[1] < 0:
            return False

    # This part of the function essentially finds the minimum number of players we could possibly take and still legally
    # have a team. If we take a player that makes it so that we cannot have a legal team anymore, False will be
    # returned. For example, if we have no RB's yet, and only two spots left on the team, we cannot take another player
    # that is not an RB since we need a minimum of two RB's for a legal team.
    min_players_needed = 0
    for key in team_restrictions:
        if team_restrictions[key][0] > 0:
            min_players_needed += team_restrictions[key][0]
    if 16 - len(roster.index) <= min_players_needed:
        return False

    # If we've made it this far, then adding this player won't violate any rules
    return True


def build_optimal_team(roster, available_players):
    """
    This method takes in the current roster, as well as the list of available players to choose from. The list of
    available players is sorted in descending order by the number of points each player earned in the MC simulation. The
    method then moves through the dataframe, picking off the highest scoring players. If the player can legally be added
     to the team, the player is added. Otherwise, we move on to the next player until we have a full team.

    :param roster: pandas dataframe with players currently on the fantasy team
    :param available_players: pandas dataframe with all available players (including points earned in MC simulation)
    :return: pandas dataframe with full roster of optimized team
    """

    current_roster = roster.copy(deep=True)
    # First, sort the players in descending order by the points they earned in the MC simulation
    available_players = available_players.sort_values(by='points', ascending=False)

    for index, row in available_players.iterrows():

        # If we can legally add this player, add them to the roster
        if can_add_player(current_roster, row['position']):
            current_roster.loc[index] = [row['full_name'], row['team'], row['position'], row['points'], row['player_object']]

        # If the size of the team is 16, the team is full
        if len(current_roster.index) >= 16:
            return current_roster
    return current_roster


def remove_undesired_players(players):
    """
    This method prompts the user to select any players that they know they do not want on their fantasy team.

    :param players: list of all Players (essentially nflgame.players)
    :return: list of all Players minus players that the user does not want on their team
    """

    # Prompt the user for player names they would like to remove
    print('Are there any players you absolutely do not want on your team? ')
    player_to_remove = raw_input('Enter player name: ')

    # If the user has entered something...
    while player_to_remove:

        # Make sure we have the right player
        player_to_remove = validate_player(player_to_remove)

        # If we have the right player, remove them
        if player_to_remove:
            try:
                players.remove(player_to_remove)
            except:
                print('Could not find '+str(player_to_remove))
        else:
            print('Could not find player.')

        # Reprompt user for more players to remove
        player_to_remove = raw_input('Enter player name: ')

    return players

def get_desired_players(all_available_players):
    """
    This method prompts the user for players that they know they want on their fantasy team.

    :param all_available_players: list of all Players that the user can pick
    :return: list of Players that the user has picked, list of Players that are remaining to be picked
    """

    # Initialize empty players list that will contains the players the user picks
    players = []

    # Prompt user for player names
    print('Are there any players you know you want on your team? (blank if none)')
    new_player = raw_input('Enter player name: ')

    # If the user has entered a name...
    while new_player:

        # Make sure we have the right player
        new_player = validate_player(new_player)

        # If we have the right player...
        if new_player:

            # and we are legally allowed to add this player to the team, add them
            if can_add_player(players_to_df(players, 0), new_player.position):
                players.append(new_player)
                all_available_players.remove(new_player)
            else:
                print('Cannot add player.')
        else:
            print('Could not find player. Please try again.')

        # Reprompt user for more players to add to team
        new_player = raw_input('Enter player name: ')

    # Remind user which players they have selected
    print('Your team so far is: ')
    for player in players:
        print(player.full_name + ', ' + player.team)

    return players, all_available_players


if __name__ == "__main__":
    # First, get a list of all the active players
    all_available_players = get_active_players()

    # Now find which players the user knows they want on their team
    user_desired_players, all_available_players = get_desired_players(all_available_players)

    # Allow the user to remove undesirable players
    all_available_players = remove_undesired_players(all_available_players)

    # Prompt the user for the # of MC simulations to be run for each player (more is better but more time consuming)
    N = int(raw_input('How many simulations should be averaged? '))

    # Initialize empty roster
    roster = pd.DataFrame(columns=['full_name','team','position','points','player_object'])

    # Add the user-selected players to the roster
    for p in user_desired_players:
        roster.loc[p.player_id] = [p.full_name, p.team, p.position, simulate([p], N), p]

    # Turn the list of available players into a df with the MC simulation points
    all_available_players_df = players_to_df(all_available_players, N)

    # Use the available players df to construct an optimal team
    roster = build_optimal_team(roster, all_available_players_df)

    # Record the roster for later access and print
    roster = roster.sort_values(by='points', ascending=False)
    roster.to_csv(str(N)+'_iter_sim')
    print(tabulate(roster, headers='keys', tablefmt='psql'))
