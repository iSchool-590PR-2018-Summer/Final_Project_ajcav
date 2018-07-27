import pandas as pd
import numpy as np
from tabulate import tabulate
import lineup_optimizer
import nflgame


def format_optimal_roster(user_roster, optimal_roster):
    """
    This method takes in the users roster and the optimal roster and marks which optimal players have already been
    picked by the user. This is only to make it easier for the user to visualize who they have picked when the df is
    printed.

    :param user_roster: pandas dataframe with players currently on the fantasy team
    :param optimal_roster: pandas dataframe with the optimal roster
    :return: pandas dataframe containing optimal roster with user-picked players indicated
    """

    # Create copies of the df so as to not change the original
    uro = user_roster.copy(deep=True)
    opt = optimal_roster.copy(deep=True)

    # Go through each player in the users rosters and marked the players that have been picked
    opt['picked'] = ''
    for index, row in opt.iterrows():
        if index in uro.index:
            opt.loc[index,'picked'] = 'Y'
    return opt


if __name__ == "__main__":
    # Get name of file to use from user
    filename = raw_input('Enter name of file to use (should have all players): ')

    # Load file into csv
    available_players = pd.read_csv(filename).set_index('player_id')

    # Initialize empty rosters
    user_roster = pd.DataFrame(columns=['full_name', 'team', 'position', 'points', 'player_object'])
    optimal_roster = pd.DataFrame(columns=['full_name', 'team', 'position', 'points', 'player_object'])

    # Begin the draft
    draft = True
    while draft:

        # Get the players picked by other league members
        picked_player_name = raw_input('Which player was picked? ')
        while picked_player_name:

            # Remove the picked players from the available players
            player_to_remove = lineup_optimizer.validate_player(picked_player_name)
            while not player_to_remove:
                print('Could not find player '+str(picked_player_name))
                picked_player_name = raw_input('Which player was picked? ')
                player_to_remove = lineup_optimizer.validate_player(picked_player_name)
            available_players = available_players.drop(player_to_remove.player_id)
            picked_player_name = raw_input('Which player was picked? ')

        # Build optimal roster and display to user
        optimal_roster = lineup_optimizer.build_optimal_team(user_roster, available_players)
        print('Optimal roster: ')
        print(tabulate(format_optimal_roster(user_roster,optimal_roster), headers='keys', tablefmt='psql'))

        # Get the users pick
        picked_player_name = raw_input('Who do you pick? ')
        picked_player = lineup_optimizer.validate_player(picked_player_name)
        while not picked_player:
            print('Could not find '+str(picked_player_name))
            picked_player_name = raw_input('Who do you pick? ')
            picked_player = lineup_optimizer.validate_player(picked_player_name)

        # Show the user their roster
        print('Your current roster: ')
        user_roster = user_roster.append(available_players.loc[picked_player.player_id])
        print(tabulate(user_roster, headers='keys', tablefmt='psql'))
