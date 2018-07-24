import nflgame

def get_team():
    players = []
    new_player = raw_input('Enter player name: ')
    while new_player:
        new_player = validate_player(new_player)
        if new_player:
            players.append(new_player)
        else:
            print('Could not find player. Please try again.')
        new_player = raw_input('Enter player name: ')
    print('Your team is: ')
    for player in players:
        print(player.full_name)
    return players


def validate_player(player):
    matches = nflgame.find(player)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    print('Found '+str(len(matches))+' for '+player+'.')
    print('Please select from the following options.')
    for i in range(len(matches)):
        print('('+str(i+1)+') - '+player+', '+matches[i].team+', number '+str(matches[i].number))
    selection = int(raw_input('Enter your selection: '))
    return matches[selection-1]



if __name__ == "__main__":
    get_team()