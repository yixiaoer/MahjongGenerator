from collections import deque
from typing import TypedDict

from basic_rules import check_legal_hand, count_identical_tiles, find_chow_tiles, find_identical_tiles, find_tiles_in_tiles
from tiles import MahjongTile, WindPosition
from utils import input_player_action

class ActionPlayer(TypedDict):
    player_idx: int  # -1 when setup
    chow: list[list[MahjongTile]]
    hu: dict[WindPosition, list[list[MahjongTile]]]
    kong: dict[WindPosition, MahjongTile | list[MahjongTile | list[MahjongTile]]]
    pong: dict[WindPosition, list[MahjongTile]]

class MahjongPlayer:
    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.tiles_hold: list[MahjongTile] = []
        self.tiles_discard: list[MahjongTile] = []
        self.position: None | WindPosition = None
        self.is_dealer: bool = False
        # if check other players, it can only be one tiles_seq, so it's the only one `list[MahjongTile]``
        # if check self, it can be a tiles_seq of concealed kong `list[MahjongTile]`, or one element `MahjongTile` for kong from pong.
        # contain some declared melds
        self.pong: list[list[MahjongTile]] = []
        self.kong: list[list[MahjongTile]] = []
        self.chow: list[list[MahjongTile]] = []

    def call_hu_from_discard(self, hu_tiles: dict[WindPosition, list[list[MahjongTile]]], tile: MahjongTile, other_player_idx: int) -> None:
        print(f'Player{self.idx} Call Hu {hu_tiles} from discard tile {tile}. Hu!')
        print(f'The discard tile is from Player{other_player_idx}.')

    def call_hu_from_wall(self, hu_tiles: dict[WindPosition, list[list[MahjongTile]]], tile: MahjongTile) -> None:
        print(f'Player{self.idx} Call Self-draw Hu {hu_tiles} with {tile} from wall. Hu!')

    def choose_action(self, pos_actions: ActionPlayer) -> None | int | str:
        print(pos_actions)
        hu_bool = False if pos_actions['hu'] == None or list(pos_actions['hu'].values()) in ([], [[]]) else True
        kong_bool = False if pos_actions['kong'] == None or list(pos_actions['kong'].values()) in ([], [[]]) else True
        pong_bool = False if pos_actions['pong'] == None or list(pos_actions['pong'].values()) in ([], [[]]) else True
        chow_bool = False if pos_actions['chow'] in (None, [], [[]]) else True
        print(f'hu_bool: {hu_bool}')
        print(f'kong_bool: {kong_bool}')
        print(f'pong_bool: {pong_bool}')
        print(f'chow_bool: {chow_bool}')
        if not (hu_bool or kong_bool or pong_bool or chow_bool):
            # if can not choose any action
            return None
        return input_player_action(hu_bool, kong_bool, pong_bool, chow_bool, pos_actions['chow'])

    def declare_chow(self, player_chow_seq: list[list[MahjongTile]], tile: MahjongTile) -> None:
        """
        This play declare Chow. The chow seq move, from hand `self.tiles_hold` and discard tile, to declared `self.chow` list.

        Returns:
            list: None.
        """
        print(f'debug chow: player_chow_seq{player_chow_seq}')
        tiles_seq = player_chow_seq[0]
        print(f'Player{self.idx} Declare Chow {tiles_seq}')

        for tile_chow in tiles_seq:
            if tile_chow != tile:
                self.tiles_hold.remove(tile_chow)
                self.tiles_discard.append(tile_chow)

        self.chow.append(tiles_seq)
        print(f'Current declared chow: {self.chow}')

    def declare_concealed_kong(self, tiles: deque[MahjongTile], kong_seq: list[MahjongTile]) -> None:
        # In Mahjong game, the Concealed Kong tile should not be shown to others. Here print the kong seq for debugging.
        print(f'Player{self.idx} Concealed Kong {kong_seq}.')
        for _ in range(4):
            self.tiles_hold.remove(kong_seq[0])
        self.kong.append(kong_seq)
        print(f'Current declared kong: {self.kong}')

        if len(tiles) > 0:
            # Draw from the other side after kong
            draw_tile = tiles.pop()
            print(f'Player{self.idx} draws {draw_tile} from the other side of the wall')
            self.tiles_hold.append(draw_tile)

    def declare_exposed_kong(self, tiles: deque[MahjongTile], tile: MahjongTile) -> None:
        tiles_seq = [tile] * 4
        print(f'Player{self.idx} Declare Exposed Kong {tiles_seq}')
        for _ in range(3):
            self.tiles_hold.remove(tile)
            self.tiles_discard.append(tile)

        self.kong.append(tiles_seq)
        print(f'Current declared kong: {self.kong}')

        if len(tiles) > 0:
            # Draw from the other side after kong
            draw_tile = tiles.pop()
            print(f'Player{self.idx} draws {draw_tile} from the other side of the wall')
            self.tiles_hold.append(draw_tile)

    def declare_exposed_kong_from_pong(self, tiles: deque[MahjongTile], kong_seq: MahjongTile) -> None:
        tiles_seq = [kong_seq] * 4
        print(f'Player{self.idx} Declare Kong {tiles_seq} from Pong.')
        self.tiles_hold.remove(kong_seq)
        self.pong.remove([kong_seq] * 3)
        self.kong.append(tiles_seq)
        print(f'Current declared kong: {self.kong}')
        print(f'Current declared pong: {self.pong}')

        if len(tiles) > 0:
            # Draw from the other side after kong
            draw_tile = tiles.pop()
            print(f'Player{self.idx} draws {draw_tile} from the other side of the wall')
            self.tiles_hold.append(draw_tile)

    def declare_pong(self, tile: MahjongTile) -> None:
        tiles_seq = [tile] * 3
        print(f'Player{self.idx} Declare Pong {tiles_seq}')
        for _ in range(2):
            self.tiles_hold.remove(tile)
            self.tiles_discard.append(tile)

        self.pong.append(tiles_seq)
        print(f'Current declared pong: {self.pong}')

    def discard_tile(self, tile: MahjongTile) -> None:
        self.tiles_hold.remove(tile)
        self.tiles_discard.append(tile)

    def draw_tiles(self, tiles: deque[MahjongTile], draw_num: int = 1) -> MahjongTile:
        for _ in range(draw_num):
            if len(tiles) > 0:
                draw_tile = tiles.popleft()
                print(f'Player{self.idx} draws {draw_tile}')
                self.tiles_hold.append(draw_tile)
        print(f'Player{self.idx} holds {self.tiles_hold}')
        return draw_tile

def check_chow(tiles_hold: list[MahjongTile], tile: MahjongTile) -> list[list[MahjongTile]]:
    is_chow_contain = False
    if tile in tiles_hold:
        is_chow_contain = True

    chow_tiles = find_chow_tiles(tiles_hold, tile)
    if not is_chow_contain: 
        tiles_hold.remove(tile)

    print(f'debug chow, tiles_hold: {tiles_hold}, tile: {tile}, check_chow_tiles:{chow_tiles}')

    if len(chow_tiles) == 0:
        return []
    return chow_tiles

def check_concealed_kong(tiles_hold: list[MahjongTile]) -> list[list[MahjongTile]]:
    kong_seqs = count_identical_tiles(tiles_hold)

    print(f'debug check_concealed_kong, tiles_hold: {tiles_hold}, check_kong_tiles:{kong_seqs}')

    if len(kong_seqs) == 0:
        return []
    return kong_seqs

def check_exposed_kong(tiles_hold: list[MahjongTile], tile: MahjongTile) -> None | MahjongTile:
    print(f'--------------check_exposed_kong tiles_hold:{tiles_hold}, tile: {tile}, {find_identical_tiles(tiles_hold, tile)}')
    if find_identical_tiles(tiles_hold, tile) == 4:
        print(f'debug check_exposed_kong, tiles_hold: {tiles_hold}, check_kong_tiles:{tile}')
        return tile
    return None

def check_exposed_kong_from_pong(tiles_hold: list[MahjongTile], pong: list[list[MahjongTile]]) -> list[MahjongTile]:
    if len(pong) == 0:
        return []
    declare_pong_tiles = [tiles[0] for tiles in pong]
    kong_from_pong_seqs = list(find_tiles_in_tiles(tiles_hold, declare_pong_tiles))
    if len(kong_from_pong_seqs) == 0:
        return []
    print(f'Can exposed kong from pong in: {kong_from_pong_seqs}')
    return kong_from_pong_seqs

def check_hu_from_discard(tiles_hold: list[MahjongTile], tile_discard: None | MahjongTile = None) -> list[list[MahjongTile]]:
    # check tiles held in hand (usually after draw tiles) when tile_discard is None
    # check tiles held in hand and with discarded one tile when tile_discard is not None
    check_tiles = tiles_hold.copy() if tile_discard is None else tiles_hold.copy() + [tile_discard]
    # if complete legal hand, legal_hand is list[list[MahjongTile]], else []
    legal_hand = check_legal_hand(check_tiles)
    return legal_hand

def check_hu_from_wall(tiles_hold: list[MahjongTile]) -> list[list[MahjongTile]]:
    legal_hand = check_legal_hand(tiles_hold)
    if len(legal_hand) > 0:
        print(f'Can self-hu from wall: {legal_hand}')
    return legal_hand

def check_pong(tiles_hold: list[MahjongTile], tile: MahjongTile) -> list[MahjongTile]:
    print(f'====================tiles_hold:{tiles_hold}, tile: {tile}, {find_identical_tiles(tiles_hold, tile)}')
    if find_identical_tiles(tiles_hold, tile) == 3:
        print(f'debug check_pong, tiles_hold: {tiles_hold}, check_pong_tiles:{tile}')
        return [tile] * 3
    return []
