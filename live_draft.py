import pandas as pd
import numpy as np
from tabulate import tabulate
import lineup_optimizer
import nflgame
import os.path


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
            opt.loc[index, 'picked'] = 'Y'
    return opt


if __name__ == "__main__":
    # Get name of file to use from user
    while True:
        filename = raw_input('Enter name of file to use (should have all players): ')
        if os.path.isfile(filename):
            break
        else:
            print('Could not find file: '+filename)

    # Load pandas df from csv
    available_players = pd.read_csv(filename).set_index('player_id')

    # Initialize empty rosters
    user_roster = pd.DataFrame(columns=['full_name', 'team', 'position', 'points', 'player_object'])
    optimal_roster = pd.DataFrame(columns=['full_name', 'team', 'position', 'points', 'player_object'])

    # Begin the draft
    draft = True
    while draft:

        # Get the players picked by other league members
        picked_player_name = raw_input('Player picked by other league member: (empty line to continue) ')
        while picked_player_name:

            # Remove the picked players from the available players
            player_to_remove = lineup_optimizer.validate_player(picked_player_name)
            while not player_to_remove:
                print('Could not find player '+str(picked_player_name))
                picked_player_name = raw_input('Player picked by other league member: ')
                if picked_player_name == '':
                    break
                player_to_remove = lineup_optimizer.validate_player(picked_player_name)
            if picked_player_name == '':
                break
            available_players = available_players.drop(player_to_remove.player_id)
            picked_player_name = raw_input('Player picked by other league member: ')

        # Build optimal roster and display to user
        optimal_roster = lineup_optimizer.build_optimal_team(user_roster, available_players)
        print('Optimal roster: ')
        print(tabulate(format_optimal_roster(user_roster,optimal_roster), headers='keys', tablefmt='psql'))

        # Get the users pick
        picked_player = None
        while not picked_player:
            picked_player_name = raw_input('Who do you pick? (empty line to skip) ')
            picked_player = lineup_optimizer.validate_player(picked_player_name)
            if picked_player_name == '':
                break
            if picked_player is None:
                print('Could not find '+picked_player_name)
                continue

            # Determine if we can add this player before adding them
            if lineup_optimizer.can_add_player(user_roster, picked_player.position):
                user_roster = user_roster.append(available_players.loc[picked_player.player_id])
            else:
                print('Cannot add another '+str(picked_player.position))
                picked_player = None

        # Show the user their roster
        print('Your current roster: ')
        print(tabulate(user_roster, headers='keys', tablefmt='psql'))

        # Check if the draft is over
        if len(user_roster.index) >= 16:
            draft = False
            print('Draft complete.')
