from __future__ import annotations

from enum import Enum
import random
from typing import Any

class WindPosition(Enum):
    EAST = 0
    SOUTH = 1
    WEST = 2
    NORTH = 3

    def __add__(self, other: Any) -> WindPosition:
        if isinstance(other, int):
            return WindPosition((self.value + other) % 4)
        raise NotImplementedError('Not supported.')

    def __sub__(self, other: Any) -> int:
        # use to calculate the 'distance' between the dealer and other players
        if isinstance(other, WindPosition):
            return (other.value - self.value) % 4
        raise NotImplementedError('Not supported.')

class MahjongTile:
    def __init__(self, tile_type: str, number: int) -> None:
        # Which tile
        self.tile_type: str = tile_type
        self.number: int = number
        # Where is the tile in game
        self.wall_pos: None | WindPosition = None
        self.wall_idx: None | int = None

    @staticmethod
    def get_tiles_from_string(tile_str: str) -> MahjongTile:
        tile_type_name = ''.join((i for i in tile_str if not i.isdigit()))
        number = int(''.join((i for i in tile_str if i.isdigit())))
        return MahjongTile(tile_type_name, number)

    def __add__(self, other: Any) -> MahjongTile:
        # TODO: modification for bonus and flowers
        if isinstance(other, int):
            num = self.number + other
            if num <= 9 and self.tile_type in ['bamboo', 'characters', 'dots']:
                return MahjongTile(self.tile_type, num)
            return MahjongTile(self.tile_type, num % 9)
        raise NotImplementedError('Not supported.')

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MahjongTile):
            return self.tile_type == other.tile_type and self.number == other.number
        elif isinstance(other, tuple) and isinstance(other[0], str) and isinstance(other[1], int):
            return self.tile_type == other[0] and self.number == other[1]
        raise NotImplementedError('Not supported.')

    def __hash__(self) -> int:
        return hash((self.tile_type, self.number))

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, MahjongTile):
            return (self.tile_type, self.number) < (other.tile_type, other.number)
        raise NotImplementedError('Not supported.')

    def __repr__(self) -> str:
        return f'{self.tile_type}{self.number}'

def shuffle_tiles(options_config: dict[str, bool]) -> list[MahjongTile]:
    """
        Shuffle all tiles with tile type config.

        Returns:
            None.
    """
    tiles = []
    if options_config['suited']:
        for tile_type in ['bamboo', 'characters', 'dots']:
            for number in range(1, 10):
                tiles += [MahjongTile(tile_type, number) for _ in range(4)]

    if options_config['honors']:
        # winds1: East, winds2: South, winds3: West, winds4: North
        # dragons1: Red, dragons2: Green, dragons3: White
        for tile_type, numbers in [('dragons', range(1, 4)), ('winds', range(1, 5))]:
            tiles += [MahjongTile(tile_type, number) for number in numbers for _ in range(4)]

    if options_config['bonus']:
        # flowers1: Plum blossom, flowers2: Orchid, flowers3: Bamboo, flowers4: Chrysanthemum
        # seasons1: Spring, seasons2: Summer, seasons3: Autumn, seasons4: Winter
        for tile_type in ['flowers', 'seasons']:
            tiles += [MahjongTile(tile_type, number) for number in range(1, 5)]

    # shuffle tiles
    random.shuffle(tiles)
    return tiles
