import nflgame
import numpy as np
import pandas as pd


def get_desired_players(all_available_players):
    players = []
    print('Are there any players you know you want on your team? (blank if none)')
    new_player = raw_input('Enter player name: ')
    while new_player:
        new_player = validate_player(new_player)
        if new_player:
            if validate_team(players, new_player):
                players.append(new_player)
                all_available_players.remove(new_player)
        else:
            print('Could not find player. Please try again.')
        new_player = raw_input('Enter player name: ')
    print('Your team is: ')
    for player in players:
        print(player.full_name+', '+player.team)
    return players, all_available_players


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


def get_active_players():
    all_players = nflgame.players
    available_players = []
    for p in all_players:
        if all_players[p].status == 'ACT':
            available_players.append(all_players[p])
    return available_players

def score_to_fantasy_points(player):
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

    points = 0.0
    for stat in player._stats:
        if stat in point_conversion.keys():
            points += point_conversion[stat](getattr(player, stat))
    return points


def get_player_score(player):
    i = 0
    while i < 50:
        i += 1
        year = np.random.choice([2014, 2015, 2016, 2017], p=[0.1, .15, .25, .5])
        week = np.random.randint(1, 18)
        games = nflgame.games(year, week=week)
        games = nflgame.combine_game_stats(games)

        for person in games:
            if person.player is None:
                continue
            if player == person.player:
                return score_to_fantasy_points(person)
    return -float('Inf')
        #return get_player_score(player)


def simulate(team, N=100):
    """
    This function runs a Monte Carlo simulation by selecting a random year (weighted heuristically since more recent
    years are a better reflection of player ability) and random week to sample a players fantasy score. The average
    score for a player is averaged over N simulations, then added to the team score. The total team score is returned.

    :param team: list of Player objects
    :param N: number of simulations to run
    :return: total points for team
    """

    total_score = 0.0
    for player in team:
        simulation_score = []
        for i in range(N):
            simulation_score.append(get_player_score(player))
        total_score += np.mean(simulation_score)
    return total_score


def players_to_df(players):
    df = pd.DataFrame(columns=['full_name','team','position','points','player_object'])
    for index, p in enumerate(players):
        print('Simulating player '+str(index+1)+' of '+str(len(players)))
        df.loc[p.player_id] = [p.full_name, p.team, p.position, simulate([p], N), p]
    return df


def can_add_player(roster, new_position):
    team_restrictions = {'QB': 4,
                         'RB': 8,
                         'WR': 8,
                         'TE': 3,
                         'K': 3,
                         'D/ST': 3,
                         'FLEX': 1}



    for index, row in roster.iterrows():
        if row['position'] in team_restrictions.keys():
            team_restrictions[row['position']] -= 1
    if new_position in team_restrictions.keys():
        team_restrictions[position] -= 1
    for v in team_restrictions.values():
        if v < 0:
            return False
    return True

def build_optimal_team(current_roster, available_players):
    available_players = available_players.sort_values(by='points')
    for index, row in available_players.iterrows():
        if can_add_player(current_roster, row['position']):
            current_roster.loc[index] = [row['full_name'], row['team'], row['position'], row['points'], row['player_object']]
        if len(current_roster.index) >= 16:
            return current_roster
    return current_roster


if __name__ == "__main__":
    all_available_players = get_active_players()
    user_desired_players, all_available_players = get_desired_players(all_available_players)
    N = int(raw_input('How many simulations should be averaged? '))
    roster = pd.DataFrame(columns=['full_name','team','position','points','player_object'])
    for p in user_desired_players:
        roster.loc[p.player_id] = [p.full_name, p.team, p.position, simulate([p], N), p]

    all_available_players_df = players_to_df(all_available_players[:10])
    roster = build_optimal_team(roster, all_available_players_df)
    print(roster)