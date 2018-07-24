import nflgame


def get_team():
    players = []
    new_player = raw_input('Enter player name: ')
    while new_player:
        new_player = validate_player(new_player)
        if new_player:
            if validate_team(players, new_player):
                players.append(new_player)
        else:
            print('Could not find player. Please try again.')
        new_player = raw_input('Enter player name: ')
    print('Your team is: ')
    for player in players:
        print(player.full_name+', '+player.team)
    return players


def validate_team(players, addition):
    team_restrictions = {'QB': 4,
                         'RB': 8,
                         'WR': 8,
                         'TE': 3,
                         'K': 3,
                         'D/ST': 3}

    potential_team = players + [addition]
    if len(potential_team) >= 16:
        print('Cannot add player. Team is already full.')
        return False

    for player in potential_team:
        if player.position in team_restrictions.keys():
            team_restrictions[player.position] -= 1
            if team_restrictions[player.position] < 0:
                print('Cannot add another '+player.position)
                return False
    return True


def validate_player(player):
    matches = nflgame.find(player)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    print('Found '+str(len(matches))+' matches for '+player.title()+'.')
    print('Please select from the following options.')
    for i in range(len(matches)):
        print('('+str(i+1)+') - '+player.title()+', '+matches[i].team+', number '+str(matches[i].number))
    selection = int(raw_input('Enter your selection: '))
    return matches[selection-1]

def simulate(team, N=1000):
    """
    This function runs a Monte Carlo simulation by selecting a random year (weighted heuristically since more recent
    years are a better reflection of player ability) and random week to sample a players fantasy score. The average
    score for a player is averaged over N simulations, then added to the team score. The total team score is returned.

    :param team: list of Player objects
    :param N: number of simulations to run
    :return: total points for team
    """

    return 1


if __name__ == "__main__":
    players = get_team()
    points = simulate(players)
