from collections import deque
import random

from player import ActionPlayer, MahjongPlayer, check_chow, check_concealed_kong, check_exposed_kong, check_exposed_kong_from_pong, check_hu_from_discard, check_hu_from_wall, check_pong
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

    def check_current_player(self, current_player: MahjongPlayer, action_choices: dict[WindPosition, ActionPlayer], draw_tile: None | MahjongTile) -> None:
        cur_pos = self.find_position(current_player)
        pos_actions = action_choices[cur_pos]
        pos_actions['player_idx'] = current_player.idx

        # when check hu, the hu_tiles should contain that draw_tile
        action_hu = check_hu_from_wall(current_player.tiles_hold)
        print(f'debug hu from draw: action_hu{action_hu}')
        if action_hu != [] and action_hu and draw_tile:
            pos_actions['hu'] = {cur_pos: action_hu}  # the value of the key 'hu' is the completed legal hand

        # when check kong, draw_tile can be None
        action_kong = check_concealed_kong(current_player.tiles_hold)
        action_kong_from_pong = check_exposed_kong_from_pong(current_player.tiles_hold, current_player.pong)
        action_kong.extend(action_kong_from_pong)  # type: ignore
        print(f'debug kong from draw: action_kong{action_kong}')

        if action_kong != [] and action_kong:
            pos_actions['kong'] = {cur_pos: action_kong}  # type: ignore
        action = current_player.choose_action(pos_actions)
        if action in {'hu', 'h'} and draw_tile:
            self.hu_from_wall(pos_actions, draw_tile)
        elif action in {'kong', 'k'}:
            self.kong_from_wall(current_player, pos_actions)

    def check_other_players(self, current_player: MahjongPlayer, tile_to_discard: MahjongTile, action_choices: dict[WindPosition, ActionPlayer]) -> None:
        if isinstance(current_player.position, WindPosition):
            cur_pos = self.find_position(current_player)
            for player in self.players:
                if player != current_player:
                    pos_actions = action_choices[self.find_position(player)]
                    pos_actions['player_idx'] = player.idx
                    print(f'Player{player.idx} check action options.')
                    action_hu = check_hu_from_discard(player.tiles_hold, tile_to_discard)
                    if action_hu != [] and action_hu:
                        pos_actions['hu'] = {cur_pos: action_hu}  # the value of the key 'hu' is the completed legal hand
                    kong_tile = check_exposed_kong(player.tiles_hold, tile_to_discard)
                    if kong_tile:
                        pos_actions['kong'] = {cur_pos: [kong_tile] * 4}
                        # also as an action to pong
                        pos_actions['pong'] = {cur_pos: [kong_tile] * 3}
                    action_pong = check_pong(player.tiles_hold, tile_to_discard)
                    if action_pong != [] and action_pong:
                        pos_actions['pong'] = {cur_pos: action_pong}
                    # Next player, check hu, kong, pong, and chow
                    if player.position == current_player.position + 1:
                        pos_actions['chow'] = check_chow(player.tiles_hold, tile_to_discard)
                    action = player.choose_action(pos_actions)
                    print(f'debug action selections: action: {action}, {type(action)}')
                    if action in {'hu', 'h'}:
                        action_choices[self.find_position(player)] = ActionPlayer(player_idx=pos_actions['player_idx'], chow=[], hu=pos_actions['hu'], kong={}, pong={})
                    elif action in {'kong', 'k'}:
                        action_choices[self.find_position(player)] = ActionPlayer(player_idx=pos_actions['player_idx'], chow=[], hu={}, kong=pos_actions['kong'], pong={})
                    elif action in {'pong', 'p'}:
                        action_choices[self.find_position(player)] = ActionPlayer(player_idx=pos_actions['player_idx'], chow=[], hu={}, kong={}, pong=pos_actions['pong'])
                    elif isinstance(action, int):
                        print(f'debug {[pos_actions['chow'][action]]}')
                        action_choices[self.find_position(player)] = ActionPlayer(player_idx=pos_actions['player_idx'], chow=[pos_actions['chow'][action]], hu={}, kong={}, pong={})
                    elif action in {'skip', 's', ''}:
                        action_choices[self.find_position(player)] = ActionPlayer(player_idx=pos_actions['player_idx'], chow=[], hu={}, kong={}, pong={})
                    print(pos_actions)
            print(action_choices)
            self.decide_other_player_action(current_player.position, action_choices, tile_to_discard)

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

    def chow(self, player_chow_pos: WindPosition, player_chow_seq: list[list[MahjongTile]], tile: MahjongTile) -> None:
        """
        Chow.

        Returns:
            list: None.
        """
        if self.position_players is not None:
            player_chow = self.position_players[player_chow_pos]
            player_chow.declare_chow(player_chow_seq, tile)
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

            # draw 13 tiles for every player, 4 * (4 -1 ) + 1 = 13
            for i in range(4):
                # decide the position to draw tiles
                for idx_pos in range(players_num):
                    player = self.position_players[self.current_position + idx_pos]
                    # draw 1 stack(4 tiles) until all players have 12 tiles
                    # draw one last tile
                    player.draw_tiles(self.tiles, 4) if i !=3 else player.draw_tiles(self.tiles)
            # draw one more tile for dealer to have 14 tiles, and no need for the dealer to draw tile at the beginning of the round with 14 tiles in hand
            self.position_players[self.dealer_position].draw_tiles(self.tiles)
            self.draw_tile_bool = False

            # decide joker tile
            joker_c = self.options_config['joker']
            # if joker_c is bool, both isinstance(joker_c, int) and isinstance(joker_c, bool) are True
            # Here if joker_c is bool and False, the game doesn't use joker tile.
            if joker_c and isinstance(joker_c, int):
                draw_for_joker = self.tiles.popleft()
                print(f'Draw one more from the wall: {draw_for_joker}. \nThe joker tile in the game: {draw_for_joker + joker_c}')

            input_yes(f'Start game? (yes, default): ')

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

    def decide_other_player_action(self, current_player_pos: WindPosition, action_choices: dict[WindPosition, ActionPlayer], tile: MahjongTile) -> None:
        player_chow_seq = None
        player_kong_pos = None
        player_pong_pos = None

        for i in range(1, players_num):
            if action_choices[current_player_pos + i]['hu'] != {}:
                # Hu takes the highest priority; if multiple players can Hu, the player closest to the dealer takes precedence
                self.hu_from_discard(action_choices[current_player_pos + i]['hu'], current_player_pos + i, current_player_pos, tile)
            if action_choices[current_player_pos + i]['kong'] != {} and player_kong_pos == None:
                player_kong_pos = current_player_pos + i
            if action_choices[current_player_pos + i]['pong'] != {} and player_pong_pos == None:
                player_pong_pos = current_player_pos + i
            if action_choices[current_player_pos + i]['chow'] != []:
                player_chow_seq = action_choices[current_player_pos + i]['chow']

        # priority: kong/pong > chow
        if player_kong_pos:
            # at most 1 player can appear in the list
            self.exposed_kong(player_kong_pos, tile)
        elif player_pong_pos:
            # at most 1 player can appear in the list
            self.pong(player_pong_pos, tile)
        elif player_chow_seq:
            self.chow(current_player_pos + 1, player_chow_seq, tile)

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

    def hu_from_discard(self, hu_tiles: dict[WindPosition, list[list[MahjongTile]]],  player_hu_pos: WindPosition, current_player_pos: WindPosition, tile: MahjongTile):
        if self.position_players is not None:
            player_hu = self.position_players[player_hu_pos]
            player_hu.call_hu_from_discard(hu_tiles, tile, self.position_players[current_player_pos].idx)
            self.hu_position = player_hu_pos

    def hu_from_wall(self, pos_actions: ActionPlayer, tile: MahjongTile) -> None:
        if self.position_players is not None:
            print(f'debug hu from wall, pos_actions:{pos_actions}')
            player_hu = self.position_players[self.current_position]
            player_hu.call_hu_from_wall(pos_actions['hu'], tile)
            self.hu_position = self.current_position

    def kong_from_wall(self, current_player: MahjongPlayer, pos_actions: ActionPlayer) -> None:
        print(f'debug kong from wall, pos_actions:{pos_actions}')
        kong_seqs = pos_actions['kong'][self.current_position]
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
            draw_tile: None | MahjongTile = None
            current_player = self.position_players[self.current_position]
            if self.draw_tile_bool:
                draw_tile = current_player.draw_tiles(self.tiles)
            current_player.tiles_hold.sort(key=lambda x: f'{x.tile_type}{x.number}')
            print('==================================================================')
            print(f'Position {self.current_position}: Player {current_player.idx}\'s hand: {current_player.tiles_hold}')
            action_choices = self.reset_players_actions()
            self.check_current_player(current_player, action_choices, draw_tile)
            self.draw_tile_bool = True

            if self.tiles and self.hu_position is None:
                tiles_check = [f'{tile.tile_type}{tile.number}'for tile in current_player.tiles_hold]
                discard_tile = input_list(f'For Player{current_player.idx} Choose a tile to discard (e.g., bamboo5): ', tiles_check, 'Please enter the existing tile in your hand.')
                tile_to_discard = MahjongTile.get_tiles_from_string(discard_tile)
                print(f'decide to discard: {tile_to_discard}')
                current_player.discard_tile(tile_to_discard)
                print(f'Player{current_player.idx} discards {discard_tile}')
                # Every time one player discard one tile, must check other players
                self.check_other_players(current_player, tile_to_discard, action_choices)
                if self.draw_tile_bool:
                    self.next_player()

            if self.hu_position is not None:
                self.next_dealer()
                print(f'Finish one round!')
                print(f'The dealer for the new round is Player{self.position_players[self.dealer_position].idx} at {self.dealer_position}')
                if input_yes(f'Start next round? (yes, default): '):
                    self.set_new_round()

            if len(self.tiles) == 0:
                print(f'Draw: No Winner.')
                print(f'Start another new round with Player{self.position_players[self.dealer_position].idx} at {self.dealer_position} as dealer')
                if input_yes(f'Start next round? (yes, default): '):
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
            player.pong = []
            player.kong = []
            player.chow = []
        self.deal_starting_tiles()

    def start_game(self) -> None:
        """
        Start game: Set the first dealer and assign initial tiles to every player.

        Returns:
            None.
        """
        if self.position_players is None:
            self.determine_first_dealer()
        self.deal_starting_tiles()

    def reset_players_actions(self) -> dict[WindPosition, ActionPlayer]:
        return {pos: ActionPlayer(player_idx=-1, chow=[], hu={}, kong={}, pong={}) for pos in positions_seq}
