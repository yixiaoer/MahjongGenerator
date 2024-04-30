from collections import deque

from basic_rules import check_legal_hand, count_identical_tiles, find_chow_tiles, find_identical_tiles, find_tiles_in_tiles
from tiles import MahjongTile, WindPosition
from utils import input_player_action

class MahjongPlayer:
    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.tiles_hold: list[MahjongTile] = []
        self.tiles_discard: list[MahjongTile] = []
        self.position: None | WindPosition = None
        self.is_dealer: bool = False
        self.hu_bool: bool | list[list[MahjongTile]] = False
        # if check other players, it can only be one tiles_seq, so it's the only one `list[MahjongTile]``
        # if check self, it can be a tiles_seq of concealed kong `list[MahjongTile]`, or one element `MahjongTile` for kong from pong.
        self.action_kong_bool: bool | list[MahjongTile | list[MahjongTile]] = False
        self.action_pong_bool: bool | list[MahjongTile] = False
        self.action_chow_bool: bool | list[list[MahjongTile]] = False
        # contain some declared melds
        self.pong: list[list[MahjongTile]] = []
        self.kong: list[list[MahjongTile]] = []
        self.chow: list[list[MahjongTile]] = []

    def call_hu_from_discard(self, tile: MahjongTile, other_player_idx: int) -> None:
        if isinstance(self.hu_bool, list):
            print(f'Player{self.idx} Call Hu {self.hu_bool} from discard tile {tile}. Hu!')
            print(f'The discard tile is from Player{other_player_idx}.')

    def call_hu_from_wall(self) -> None:
        if isinstance(self.hu_bool, list):
            print(f'Player{self.idx} Call Self-draw Hu {self.hu_bool}. Hu!')

    def check_chow(self, tile: MahjongTile) -> None:
        check_chow_contain = False
        if tile in self.tiles_hold:
            check_chow_contain = True

        chow_tiles = find_chow_tiles(self.tiles_hold, tile)
        if len(chow_tiles) > 0:
            self.action_chow_bool = chow_tiles
        else:
            self.action_chow_bool = False

        if not check_chow_contain: 
            self.tiles_hold.remove(tile)

    def check_concealed_kong(self) -> None:
        kong_seqs = count_identical_tiles(self.tiles_hold)
        if len(kong_seqs) > 0:
            self.action_kong_bool = kong_seqs

    def check_exposed_kong(self, tile: MahjongTile) -> None:
        if find_identical_tiles(self.tiles_hold, tile) == 4:
            self.action_kong_bool = [tile] * 4
            self.action_pong_bool = [tile] * 3
        else:
            self.action_kong_bool = False

    def check_exposed_kong_from_pong(self) -> None:
        if len(self.pong) > 0:
            declare_pong_tiles = [tiles[0] for tiles in self.pong]
            kong_from_pong_seqs = list(find_tiles_in_tiles(self.tiles_hold, declare_pong_tiles))
            if isinstance(self.action_kong_bool, list):
                self.action_kong_bool.extend(kong_from_pong_seqs)
                print(f'Can exposed_kong_from_pong in: {kong_from_pong_seqs}')
            else:
                self.action_kong_bool = kong_from_pong_seqs

    def check_hu_from_discard(self, tile_discard: None | MahjongTile = None) -> None:
        # check tiles held in hand (usually after draw tiles) when tile_discard is None
        # check tiles held in hand and with discarded one tile when tile_discard is not None
        check_tiles = self.tiles_hold.copy() if tile_discard is None else self.tiles_hold.copy() + [tile_discard]
        legal_hand = check_legal_hand(check_tiles)
        if isinstance(legal_hand, list):
            self.hu_bool = legal_hand
        else:
            self.hu_bool = False

    def check_hu_from_wall(self) -> None:
        legal_hand = check_legal_hand(self.tiles_hold)
        if isinstance(legal_hand, list):
            self.hu_bool = legal_hand
            print('Can self-hu from wall')
            print(legal_hand)
        else:
            self.hu_bool = False

    def check_pong(self, tile: MahjongTile) -> None:
        if find_identical_tiles(self.tiles_hold, tile) == 3:
            self.action_pong_bool = [tile] * 3
        else:
            self.action_pong_bool = False

    def choose_action(self) -> None | int | str:
        hu_bool = True if self.hu_bool else False
        kong_bool = True if self.action_kong_bool else False
        pong_bool = True if self.action_pong_bool else False
        chow_bool = True if self.action_chow_bool else False
        if not (hu_bool or kong_bool or pong_bool or chow_bool):
            # if can not choose any action
            return None
        return input_player_action(hu_bool, kong_bool, pong_bool, chow_bool, self.action_chow_bool)

    def declare_chow(self, chow_idx: int, tile: MahjongTile) -> None:
        """
        This play declare Chow. The chow seq move, from hand `self.tiles_hold` and discard tile, to declared `self.chow` list.

        Returns:
            list: None.
        """
        if isinstance(self.action_chow_bool, list):
            tiles_seq = self.action_chow_bool[chow_idx]
            print(f'Player{self.idx} Declare Chow {tiles_seq}')

            for tile_chow in tiles_seq:
                if tile_chow != tile:
                    self.tiles_hold.remove(tile_chow)
                    self.tiles_discard.append(tile_chow)

            self.chow.append(tiles_seq)
            print(f'Current declared chow: {self.chow}')

    def declare_concealed_kong(self, tiles: deque[MahjongTile], kong_seq: list[MahjongTile]) -> None:
        # In Mahjang game, the Concealed Kong tile should not be shown to others. Here print the kong seq for debugging.
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
        for _ in range(2):
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

    def draw_tiles(self, tiles: deque[MahjongTile], draw_num: int = 1) -> None:
        for _ in range(draw_num):
            if len(tiles) > 0:
                draw_tile = tiles.popleft()
                print(f'Player{self.idx} draws {draw_tile}')
                self.tiles_hold.append(draw_tile)
        print(f'Player{self.idx} holds {self.tiles_hold}')
