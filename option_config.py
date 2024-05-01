from utils import input_list, input_yes_or_no

def decide_joker_config(joker: bool = False) -> bool | int :
    # TODO: Methods to determine the joker tile vary by variant. Future updates may include options to choose from. 
    # Currently, only this method is implemented:
    # After each player has drawn their initial 13 tiles and the dealer has drawn 14 tiles, draw `another tile` from the wall.
    # Joker is decided by this `another tile`.
    # Here, the descriptions are used to determine whether  the `another tile` or `another tile` + 1 is the joker.
    joker_descriptions = [
        'This drawn tile(3 left tiles with the same tile typle and number) becomes the Wild Card. ',
        'The tile succeeding this drawn one(4 tiles with the same tile type, and number + 1) becomes the Wild Card. ',
    ]

    if joker is False:
        return joker
    return int(input_list(f'Decide joker tile: {' '.join(f'{i}.{joker_descriptions[i]}' for i in range(len(joker_descriptions)))}?(Only input number) ', [f'{i}' for i in range(len(joker_descriptions))], 'Invalid chow seq.'))

def set_options_config(suited: bool = True, honors: bool = True, bonus: bool = False, joker: bool | int = False) -> dict[str, bool | int]:
    options_config = {
        'suited': suited,
        'honors': honors,
        'bonus': bonus,
        'joker': joker,
    }
    return options_config


def setup_game() -> dict[str, bool | int]:
    print('Welcome to the Mahjong Game Setup')

    # Set up the tile types
    suited = input_yes_or_no('Include basic suited (bamboo, characters, dots)? (yes/no): ')
    honors = input_yes_or_no('Include honors (dragons, winds)? (yes/no): ')
    bonus = input_yes_or_no('Include bonus(flowers, seasons)? (yes/no): ')

    # Set up joker config
    joker = input_yes_or_no('Include joker(represent any other tile to complete a legal hand)? (yes/no): ')

    options_config = set_options_config(suited, honors, bonus, decide_joker_config(joker))
    return options_config
