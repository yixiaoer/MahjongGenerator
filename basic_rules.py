from collections import Counter

from tiles import MahjongTile

def check_legal_hand(tiles: list[MahjongTile]) -> list[list[MahjongTile]]:
    if len(tiles) % 3 != 2:
        return []

    tiles_tuple = tuple(sorted((tile.tile_type, tile.number) for tile in tiles))
    tiles_counts = Counter(tiles_tuple)
    pair: list[tuple[str, int]] = []

    def try_melds_pair(start_idx: int = 0, pair_used: bool = False) -> bool:
        # The legal hand should have a pair
        if all(count == 0 for count in tiles_counts.values()):
            return pair_used

        for index in range(start_idx, len(tiles_tuple)):
            tile = tiles_tuple[index]
            count = tiles_counts[tile]
            # Try pair in hand
            if count >= 2 and not pair_used:
                tiles_counts[tile] -= 2
                if try_melds_pair(index, True):
                    pair.extend(list(tiles_tuple)[index: index + 2])
                    return True
                tiles_counts[tile] += 2
            # Try pong seq in hand
            if count >= 3:
                tiles_counts[tile] -= 3
                if try_melds_pair(start_idx, pair_used):
                    return True
                tiles_counts[tile] += 3
            # Try chow seq in hand, only try until number is 7 (since the max number is 9)
            if tile[1] <= 7:
                tile_next = (tile[0], tile[1] + 1)
                tile_nn = (tile[0], tile[1] + 2)
                if tiles_counts[tile_next] > 0 and tiles_counts[tile_nn] > 0:
                    tiles_counts[tile] -= 1
                    tiles_counts[tile_next] -= 1
                    tiles_counts[tile_nn] -= 1
                    if try_melds_pair(start_idx, pair_used):
                        return True
                    tiles_counts[tile] += 1
                    tiles_counts[tile_next] += 1
                    tiles_counts[tile_nn] += 1

        return False

    legal_hand_bool = try_melds_pair()
    if not legal_hand_bool:
        return []
    melds = remove_pairs_from_list(tiles, pair)
    return [melds, [MahjongTile(*pair[0])] * 2]

def count_identical_tiles(tiles: list[MahjongTile], count_num: int = 4) -> list[list[MahjongTile]]:
    counter = Counter(tiles)
    return [[tile] * count for tile, count in counter.items() if count == count_num]

def find_chow_tiles(tiles_hold: list[MahjongTile], tile_discard_last: MahjongTile, count: int = 3) -> list[list[MahjongTile]]:
    if tile_discard_last not in tiles_hold:
        tiles_hold += [tile_discard_last]
    tiles_hold = sorted((tile for tile in tiles_hold if tile.tile_type == tile_discard_last.tile_type), key=lambda tile: tile.number)

    # Remove duplicates
    tiles_unique: list[MahjongTile] = []
    for tile in tiles_hold:
        if not tiles_unique or tile.number != tiles_unique[-1].number:
            tiles_unique.append(tile)

    chow_tiles: list[list[MahjongTile]] = []
    if tile_discard_last.tile_type not in ['bamboo', 'characters', 'dots']:
        return chow_tiles

    for i in range(len(tiles_unique) - count + 1):
        if all(tiles_unique[i + j].number == tiles_unique[i].number + j for j in range(count)):
            seq = tiles_unique[i:i + count]
            if tile_discard_last in seq:
                chow_tiles.append(seq)

    return chow_tiles

def find_identical_tiles(tiles_hold: list[MahjongTile], tile_discard_last: MahjongTile) -> int:
    # count `tile_discard_last` in `tiles_hold`
    # if return 3: can pong; if return 4: can kong(Exposed kong)
    count_hold = sum(1 for tile in tiles_hold if tile.tile_type == tile_discard_last.tile_type and tile.number == tile_discard_last.number)
    return count_hold + 1

def find_tiles_in_tiles(source_l: list[MahjongTile], target_l: list[MahjongTile]) -> set[MahjongTile]:
    target_set = set(target_l)
    return {tile for tile in source_l if tile in target_set}

def remove_pairs_from_list(source_l: list[MahjongTile], target: list[tuple[str, int]]) -> list[MahjongTile]:
    result_l = source_l.copy()
    for item in target:
        if item in result_l:
            result_l.remove(item)  # type: ignore
    result_l.sort(key=lambda x: f'{x.tile_type}{x.number}')
    return result_l

# Test code for these basic rules
def test_check_legal_hand() -> None:
    tiles = [
            # Melds: (bamboo1, bamboo2, bamboo3); (dots9, dots9, dots9).
            # Pair: bamboo2, bamboo2.
            [
                MahjongTile('bamboo', 1), MahjongTile('bamboo', 2), MahjongTile('bamboo', 3),
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 2),
                MahjongTile('dots', 9), MahjongTile('dots', 9), MahjongTile('dots', 9),
            ],
            # Melds: (bamboo1, bamboo1, bamboo1); (bamboo2, bamboo3, bamboo4); (bamboo3, bamboo4, bamboo5); (bamboo3, bamboo4, bamboo5).
            # Pair: bamboo2, bamboo2.
            [
                MahjongTile('bamboo', 1), MahjongTile('bamboo', 1), MahjongTile('bamboo', 1),
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 2),
                MahjongTile('bamboo', 3), MahjongTile('bamboo', 3), MahjongTile('bamboo', 3),
                MahjongTile('bamboo', 4), MahjongTile('bamboo', 4), MahjongTile('bamboo', 4),
                MahjongTile('bamboo', 5), MahjongTile('bamboo', 5),
            ],
            # Melds: (bamboo3, bamboo3, bamboo3); (characters5, characters5, characters5); (dots9, dots9, dots9).
            # Pair: bamboo2, bamboo2.
            [
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 2),
                MahjongTile('bamboo', 3), MahjongTile('bamboo', 3), MahjongTile('bamboo', 3),
                MahjongTile('characters', 5), MahjongTile('characters', 5), MahjongTile('characters', 5),
                MahjongTile('dots', 9), MahjongTile('dots', 9),  MahjongTile('dots', 9)],
            # Only Pairs
            [
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 2)
            ],
            # Melds: (bamboo2, bamboo3,bamboo4); (bamboo3, bamboo3, bamboo3); (bamboo4, bamboo5, bamboo6).
            # Pair: bamboo4, bamboo4.
            [
                MahjongTile('bamboo', 4), MahjongTile('bamboo', 4),
                MahjongTile('bamboo', 3), MahjongTile('bamboo', 3), MahjongTile('bamboo', 3), 
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 3), MahjongTile('bamboo', 4),
                MahjongTile('bamboo', 4), MahjongTile('bamboo', 5),  MahjongTile('bamboo', 6),
            ],
            # 4 same tiles in 2 chow seqs and 1 pair
            # Melds: (bamboo1, bamboo2, bamboo3); (bamboo2, bamboo3, bamboo4); (bamboo4, bamboo5, bamboo6); (bamboo8, bamboo8, bamboo8).
            # Pair: bamboo4, bamboo4
            [
                MahjongTile('bamboo', 1), MahjongTile('bamboo', 2), MahjongTile('bamboo', 3),
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 3), MahjongTile('bamboo', 4),
                MahjongTile('bamboo', 4), MahjongTile('bamboo', 4), MahjongTile('bamboo', 4),
                MahjongTile('bamboo', 8), MahjongTile('bamboo', 8), MahjongTile('bamboo', 8),
                MahjongTile('bamboo', 5), MahjongTile('bamboo', 6),
            ],
    ]

    for tiles_ in tiles:
        print(check_legal_hand(tiles_))

def test_count_identical_tiles() -> None:
    tiles_hold = [MahjongTile('bamboo', 6), MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 6), 
                  MahjongTile('bamboo', 2), MahjongTile('bamboo', 6), MahjongTile('bamboo', 2), MahjongTile('bamboo', 6), 
                  MahjongTile('dots', 8)]
    identical_tiles = count_identical_tiles(tiles_hold)
    print(identical_tiles)  # [[bamboo6, bamboo6, bamboo6, bamboo6], [bamboo2, bamboo2, bamboo2, bamboo2]]

def test_find_chow_tiles() -> None:
    tiles_hold = [MahjongTile('dots',5), MahjongTile('characters', 6), MahjongTile('dots', 4), MahjongTile('dots' ,4)]
    tile_discard_last = MahjongTile('dots', 3)
    chow_tiles = find_chow_tiles(tiles_hold, tile_discard_last)
    print(chow_tiles)  # [[dots3, dots4, dots5]]

    tiles_hold = [MahjongTile('characters', 8), MahjongTile('bamboo', 2), MahjongTile('bamboo', 3), MahjongTile('bamboo', 5), MahjongTile('bamboo', 7), MahjongTile('bamboo', 6), MahjongTile('dots', 8)]
    tile_discard_last = MahjongTile('bamboo', 4)
    chow_tiles = find_chow_tiles(tiles_hold, tile_discard_last)
    print(chow_tiles)  # [[bamboo2, bamboo3, bamboo4], [bamboo3, bamboo4, bamboo5], [bamboo4, bamboo5, bamboo6]]

def test_find_identical_tiles() -> None:
    tiles_hold = [MahjongTile('characters', 8), MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 7), MahjongTile('bamboo', 6), MahjongTile('dots', 8)]
    tile_discard_last = MahjongTile('bamboo', 2)
    identical_tiles = find_identical_tiles(tiles_hold, tile_discard_last)
    print(identical_tiles)  # 4

def test_find_tiles_in_tiles() -> None:
    source_l = [MahjongTile('bamboo', 6), MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 6), 
                MahjongTile('dots', 8), MahjongTile('bamboo', 6), MahjongTile('bamboo', 2), MahjongTile('bamboo', 6)]
    target_l = [MahjongTile('bamboo', 2), MahjongTile('winds', 2), MahjongTile('dots', 8)]
    tiles = find_tiles_in_tiles(source_l, target_l)
    print(tiles)  # {bamboo2, dots8}

def test_remove_pairs_from_list() -> None:
    source_l = [MahjongTile('bamboo', 8), MahjongTile('bamboo', 2), MahjongTile('bamboo', 6), 
                MahjongTile('bamboo', 2), MahjongTile('bamboo', 2), MahjongTile('bamboo', 8)]
    target = [('bamboo', 2), ('bamboo', 2), ('bamboo', 8)]
    tiles = remove_pairs_from_list(source_l, target)
    print(tiles)  # [bamboo2, bamboo6, bamboo8]
