from utils import input_yes_or_no

def set_tile_config(suited: bool = True, honors: bool = True, bonus: bool = False) -> dict[str, bool]:
    tile_types = {
        'suited': suited,
        'honors': honors,
        'bonus': bonus,
    }
    return tile_types

def setup_game() -> dict[str, bool]:
    print('Welcome to the Mahjong Game Setup')

    suited = input_yes_or_no('Include basic suited (bamboo, characters, dots)? (yes/no): ')
    honors = input_yes_or_no('Include honors (dragons, winds)? (yes/no): ')
    bonus = input_yes_or_no('Include bonus(flowers, seasons)? (yes/no): ')

    tile_types = set_tile_config(suited, honors, bonus)
    return tile_types
