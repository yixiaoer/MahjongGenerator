from collections import deque
import random

from player import MahjongPlayer
from tiles import MahjongTile, WindPosition, shuffle_tiles
from utils import input_list, input_yes

dice_num:int = 2

players_num:int = 4

positions_seq: list[WindPosition] = [WindPosition.EAST, WindPosition.SOUTH, WindPosition.WEST, WindPosition.NORTH]

class MahjongGame:
    def __init__(self, options_config: dict[str, bool]) -> None:
        self.tiles: None | deque[MahjongTile] = None
        self.options_config: dict[str, bool] = options_config
        self.players: list[MahjongPlayer] = [MahjongPlayer(i) for i in range(players_num)]
        self.position_players: None | dict[WindPosition, MahjongPlayer] = None  # map position and player
        self.dealer_position: WindPosition = WindPosition.EAST  # The player at EAST position is the starting dealer
        self.current_position: WindPosition = self.dealer_position  # Current position in game; The starting position is the starting dealer
        self.joker: None | MahjongTile = None
        self.draw_tile_bool: bool = True
        self.hu_position: WindPosition | None = None
        self.game_over: bool = False

    def build_walls(self) -> list[MahjongTile]:
        """
        Shuffle tiles, then build wall at every table position.

        Returns:
            list: The initial tiles after shuffle.
        """
        tiles = shuffle_tiles(self.options_config)
        assert len(tiles) % 4 == 0, 'The number of tiles is not divisible by 4.'
        part_tiles_num = len(tiles) // 4
        print('After shuffling:')
        print(tiles)

        for i, position in enumerate(positions_seq):
            print(f'The tiles at position {position}')
            for idx, tile in enumerate(tiles[i * part_tiles_num : (i + 1) * part_tiles_num]):
                tile.wall_pos = position
                tile.wall_idx = idx
                print(f'Tile {tile.tile_type}{tile.number} is at {tile.wall_idx}')
        return tiles

    def check_current_player(self, current_player: MahjongPlayer) -> None:
        current_player.check_hu_from_wall()
        current_player.check_concealed_kong()
        current_player.check_exposed_kong_from_pong()
        action = current_player.choose_action()
        if action in {'hu', 'h'}:
            self.hu_from_wall()
        elif action in {'kong', 'k'}:
            self.kong_from_wall(current_player)

    def check_other_players(self, current_player: MahjongPlayer, tile_to_discard: MahjongTile) -> None:
        # no need to process 'skip'
        if isinstance(current_player.position, WindPosition):
            players_action: dict[str, list] = {'h': [], 'k': [], 'p': [], 'c': []}
            for player in self.players:
                if player != current_player:
                    print(f'Player{player.idx} check action options.')
                    player.check_hu_from_discard(tile_to_discard)
                    player.check_exposed_kong(tile_to_discard)
                    player.check_pong(tile_to_discard)
                    # Next player, check hu, kong, pong, and chow
                    if player.position == current_player.position + 1:
                        player.check_chow(tile_to_discard)
                    action = player.choose_action()
                    if action in {'hu', 'h'}:
                        players_action['h'].append(player.position)
                    elif action in {'kong', 'k'}:
                        players_action['k'].append(player.position)
                    elif action in {'pong', 'p'}:
                        players_action['p'].append(player.position)
                    elif isinstance(action, int):
                        players_action['c'].append(action)
            print(players_action)
            self.decide_other_player_action(current_player.position, players_action, tile_to_discard)
            self.set_players_bool()

    def choose_table_position(self) -> None:
        """
        Set position for every player with `self.position_players` mapping.

        Returns:
            None.
        """
        if isinstance(self.position_players, dict):
            for pos, player in self.position_players.items():
                # set dealer for the first game
                if pos == WindPosition.EAST:
                    player.is_dealer = True
                # set position for every player
                player.position = pos
                print(f'Player{player.idx} sits at position {pos}')

    def chow(self, player_chow_pos: WindPosition, chow_idx: int, tile: MahjongTile) -> None:
        """
        Chow.

        Returns:
            list: None.
        """
        if self.position_players is not None:
            player_chow = self.position_players[player_chow_pos]
            player_chow.declare_chow(chow_idx, tile)
            self.draw_tile_bool = False
            self.current_position = player_chow_pos

    def deal_starting_tiles(self) -> None:
        """
        Build walls, roll dice by the dealer, and start drawing tiles for 4 players.
        Set `self.tiles` begin with the one whose position determined by the dice.

        Returns:
            None.
        """
        if self.position_players and self.options_config:
            tiles = self.build_walls()
            print(f'before decide starting tiles position, len(tile):{len(tiles)}')
            print(tiles)
            part_tiles_num = len(tiles) // 4
            pos_num, wall_idx = self.decide_initial_draw_position()
            print(f'pos_num at {pos_num}, wall_idx at {wall_idx}')
            if pos_num % 4 == 1:
                pos_start = self.dealer_position
                pos_num = 0
            elif pos_num % 4 == 2:
                pos_start = self.dealer_position + 1
                pos_num = 1
            elif pos_num % 4 == 3:
                pos_start = self.dealer_position + 2
                pos_num = 2
            else:
                pos_start = self.dealer_position + 3
                pos_num = 3
            print(f'pos_num at {pos_start}, wall_idx at {wall_idx}')
            # Skip `wall_idx` stacks in the wall at the given position
            tiles = tiles[part_tiles_num * pos_num + wall_idx * 2 :] + tiles[0 : part_tiles_num * pos_num + wall_idx * 2]
            print(f'after decide starting tiles position, len(tile):{len(tiles)}')
            print(tiles)
            self.tiles = deque(tiles)

            # draw 13 tiles for every player
            for i in range(4):
                for player in self.players:
                    # draw 1 stack(4 tiles) until all players have 12 tiles
                    # draw one last tile
                    player.draw_tiles(self.tiles, 4) if i !=3 else player.draw_tiles(self.tiles)
            # draw one more tile for dealer to have 14 tiles, and no need for the dealer to draw tile at the beginning of the round with 14 tiles in hand
            self.position_players[self.dealer_position].draw_tiles(self.tiles)
            self.draw_tile_bool = False

            # decide joker tile
            joker_c = self.options_config['joker']
            if isinstance(joker_c, int):
                draw_for_joker = self.tiles.popleft()
                print(f'Draw one more from the wall: {draw_for_joker}. \nThe joker tile in the game: {draw_for_joker + joker_c}')

    def decide_initial_draw_position(self) -> tuple[int, int]:
        """
        Decide the initial draw position.

        Returns:
            tuple[int, int]: The sum of dice is to decide the start position, the min one of dice is to decide the stack index at that position.
        """
        input_dealer_bool = input_yes(f'To determine initial draw position, dealer roll dice? (yes, default): ')
        if input_dealer_bool:
            dice_rolls = [random.randint(1, 6) for _ in range(2)]
        pos_num, wall_idx = sum(dice_rolls), min(dice_rolls)
        return pos_num, wall_idx

    def decide_other_player_action(self, current_player_pos: WindPosition, players_action: dict[str, list[WindPosition]], tile: MahjongTile) -> None:
        if len(players_action['h']) > 0:
            player_hu_pos_relative = min(current_player_pos - pos for pos in players_action['h'])
            player_hu_pos = current_player_pos + player_hu_pos_relative
            self.hu_from_discard(player_hu_pos, current_player_pos, tile)
        elif len(players_action['k']) > 0:
            # at most 1 player can appear in the list
            player_kong_pos_relative = current_player_pos - players_action['k'][0] 
            player_kong_pos = current_player_pos + player_kong_pos_relative
            self.exposed_kong(player_kong_pos, tile)
        elif len(players_action['p']) > 0:
            # at most 1 player can appear in the list
            player_pong_pos_relative = current_player_pos - players_action['p'][0] 
            player_pong_pos = current_player_pos + player_pong_pos_relative
            self.pong(player_pong_pos, tile)
        elif len(players_action['c']) > 0:
            # at most 1 player can appear in the list, and only can be the next(pos + 1) player
            # the `action` in list should be chow index
            chow_idx = players_action['c'][0]
            if isinstance(chow_idx, int):
                self.chow(current_player_pos + 1, chow_idx, tile)

    def decide_players_position(self, dice_rolls_players: list[int]) -> None:
        """
        Decide the mapping from player to position, and set to `self.position_players`.
        The highest count takes the dealer position East, the right(second-highest) one takes South, across(3rd) is West, and the left(4th) is North.

        Args:
            dice_rolls_players: The list of totals rolled by each player.

        Returns:
            None.
        """
        sorted_players = sorted(zip(dice_rolls_players, self.players), reverse=True, key=lambda x: x[0])
        players_position = {pos: player for pos, (_, player) in zip(positions_seq, sorted_players)}
        self.position_players = players_position
        self.players = [player for _, player in sorted_players]
        print(f'Already determined the dealer: Player{players_position[WindPosition.EAST].idx}')
        print(f'self.players: {self.players}')
        self.choose_table_position()

    def determine_first_dealer(self) -> None:
        """
        Each player throws dice to decide who takes the starting dealer position.

        Returns:
            None.
        """
        dice_rolls_players = []
        for i in range(players_num):
            input_bool = input_yes(f'To determine dealer, Player {i} roll dice? (yes, default): ')
            if input_bool:
                dice_rolls = [random.randint(1, 6) for _ in range(2)]
                print(f'Player{i} roll dice: {dice_rolls}')
                dice_rolls_players.append(sum(dice_rolls))
        self.decide_players_position(dice_rolls_players)

    def exposed_kong(self, player_kong_pos: WindPosition, tile: MahjongTile) -> None:
        if self.position_players is not None and self.tiles is not None:
            player_kong = self.position_players[player_kong_pos]
            player_kong.declare_exposed_kong(self.tiles, tile)
            self.draw_tile_bool = False
            self.current_position = player_kong_pos

    def find_position(self, other_player: MahjongPlayer) -> WindPosition:
        if isinstance(self.position_players, dict):
            for pos, player in self.position_players.items():
                if player == other_player:
                    return pos
        return NotImplemented

    def hu_from_discard(self, player_hu_pos: WindPosition, current_player_pos: WindPosition, tile: MahjongTile):
        if self.position_players is not None:
            player_hu = self.position_players[player_hu_pos]
            player_hu.call_hu_from_discard(tile, self.position_players[current_player_pos].idx)
            self.hu_position = player_hu_pos

    def hu_from_wall(self) -> None:
        if self.position_players is not None:
            player_hu = self.position_players[self.current_position]
            player_hu.call_hu_from_wall()
            self.hu_position = self.current_position

    def kong_from_wall(self, current_player: MahjongPlayer) -> None:
        kong_seqs = current_player.action_kong_bool
        if isinstance(kong_seqs, list) and isinstance(self.tiles, deque):
            print(f'Self kong: {kong_seqs}')
            kong_idx = input_list(f'Which seq to kong: {' '.join(f'{i}.{kong_seqs[i]}' for i in range(len(kong_seqs)))}?(Only input number) ', [f'{i}' for i in range(len(kong_seqs))], 'Invalid Kong seq.')
            kong_seq = kong_seqs[int(kong_idx)]
            if isinstance(kong_seq, MahjongTile):
                current_player.declare_exposed_kong_from_pong(self.tiles, kong_seq)
            elif isinstance(kong_seq, list) and len(kong_seq) == 4:
                current_player.declare_concealed_kong(self.tiles, kong_seq)
            self.draw_tile_bool = False

    def next_dealer(self) -> None:
        """
        Decide the next dealer position.

        Returns:
            None.
        """
        if self.hu_position != self.dealer_position and self.position_players is not None:
            self.position_players[self.dealer_position].is_dealer = False
            self.dealer_position += 1
            self.position_players[self.dealer_position].is_dealer = True

    def next_player(self) -> None:
        """
        Jump to the next player with position.

        Returns:
            None.
        """
        self.current_position = self.current_position + 1

    def pong(self, player_pong_pos: WindPosition, tile: MahjongTile) -> None:
        if self.position_players is not None:
            player_pong = self.position_players[player_pong_pos]
            player_pong.declare_pong(tile)
            self.draw_tile_bool = False
            self.current_position = player_pong_pos

    def run(self) -> None:
        self.start_game()
        tile_to_discard = None
        while self.tiles and len(self.tiles) > 0 and self.position_players is not None and not self.game_over:
            current_player = self.position_players[self.current_position]
            if self.draw_tile_bool:
                current_player.draw_tiles(self.tiles)
            current_player.tiles_hold.sort(key=lambda x: f'{x.tile_type}{x.number}')
            print(f'Position {self.current_position}: Player {current_player.idx}\'s hand: {current_player.tiles_hold}')
            self.check_current_player(current_player)
            self.draw_tile_bool = True

            if self.tiles:
                tiles_check = [f'{tile.tile_type}{tile.number}'for tile in current_player.tiles_hold]
                discard_tile = input_list(f'For Player{current_player.idx} Choose a tile to discard (e.g., bamboo5): ', tiles_check, 'Please enter the existing tile in your hand.')
                tile_to_discard = MahjongTile.get_tiles_from_string(discard_tile)
                print(f'decide to discard: {tile_to_discard}')
                current_player.discard_tile(tile_to_discard)
                print(f'Player{current_player.idx} discards {discard_tile}')
                # Every time one player discard one tile, must check other players
                self.check_other_players(current_player, tile_to_discard)
                if self.draw_tile_bool:
                    self.next_player()

            if self.hu_position is not None:
                self.next_dealer()
                print(f'Finish one round!')
                print(f'The dealer for the new round is Player{self.position_players[self.dealer_position].idx} at {self.dealer_position}')
                self.set_new_round()

    def set_new_round(self) -> None:
        """
        Set the variables for the new round.

        Returns:
            None.
        """
        self.tiles = None
        self.current_position = self.dealer_position  # Current position in game; The starting position is the starting dealer
        self.joker = None
        self.draw_tile_bool = True
        self.hu_position =  None

        for player in self.players:
            player.tiles_hold = []
            player.tiles_discard = []
            player.hu_bool = False
            player.action_kong_bool = False
            player.action_pong_bool = False
            player.action_chow_bool = False
            player.pong = []
            player.kong = []
            player.chow = []
        self.deal_starting_tiles()

    def set_players_bool(self) -> None:
        """
        Set the variables for checking hu, kong, pong, and chow to default values.

        Returns:
            None.
        """
        for player in self.players:
            player.hu_bool = False
            player.action_kong_bool = False
            player.action_pong_bool = False
            player.action_chow_bool = False

    def start_game(self) -> None:
        """
        Start game: Set the first dealer and assign initial tiles to every player.

        Returns:
            None.
        """
        if self.position_players is None:
            self.determine_first_dealer()
        self.deal_starting_tiles()
