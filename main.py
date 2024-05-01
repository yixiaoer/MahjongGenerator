from game import MahjongGame
from option_config import setup_game

def main():
    options_config = setup_game()
    game = MahjongGame(options_config)
    game.run()

if __name__ == '__main__':
    main()
