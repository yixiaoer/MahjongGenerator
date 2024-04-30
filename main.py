from game import MahjongGame
from option_config import setup_game

def main():
    tile_types = setup_game()
    game = MahjongGame(tile_types)
    game.run()

if __name__ == '__main__':
    main()
