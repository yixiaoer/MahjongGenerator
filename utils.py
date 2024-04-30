from typing import Any
from tiles import MahjongTile

def display_bool_str(bool_l: list[bool], str_l: list[str]) -> str:
    assert len(bool_l) == len(str_l), 'bool_l and str_l must be of the same length.'
    result_str_l = [action for cond, action in zip(bool_l, str_l) if cond]
    return f'Available actions: {' '.join(result_str_l)}' if result_str_l else 'No available actions'

def input_list(description: str, check_list: list[Any], error: str) -> str:
    while True:
        input_ = input(description).lower()
        try:
            if input_ in set(check_list):
                return input_
            else:
                raise ValueError(error)
        except ValueError as e:
            print(e)

def input_player_action(hu_bool: bool, kong_bool: bool, pong_bool: bool, chow_bool: bool, chow_seqs: bool | list[MahjongTile] = False) -> None | str | int:
    while True:
        str_l = ['can "Hu"', 'can "Kong"', 'can "Pong"', 'can "Chow"']
        description = display_bool_str([hu_bool, kong_bool, pong_bool, chow_bool], str_l)
        input_ = input(f'{description}. \nChoose one or Skip(default): ').lower()
        try:
            if input_ in {'hu', 'h', 'kong', 'k', 'pong', 'p', 'chow', 'c', 'skip', 's', ''}:
                if (input_ in {'skip', 's', ''}):
                    return None
                elif (input_ in {'hu', 'h'} and hu_bool) or (input_ in {'kong', 'k'} and kong_bool) or (input_ in {'pong', 'p'} and pong_bool):
                    return input_
                elif input_ in {'chow', 'c'} and chow_bool and isinstance(chow_seqs, list):
                    if chow_seqs:
                        chow_idx = input_list(f'Which seq to chow: {' '.join(f'{i}.{chow_seqs[i]}' for i in range(len(chow_seqs)))}?(Only input number) ', [f'{i}' for i in range(len(chow_seqs))], 'Invalid chow seq.')
                        return int(chow_idx)
                else:
                    raise ValueError('Invalid action. This player does not support this operation.')
            else:
                raise ValueError("Invalid input: Expected 'hu', 'h', 'kong', 'k', 'pong', 'p', 'chow', 'c', 'skip', 's', or an empty string.")
        except ValueError as e:
            print(e)

def input_yes(description: str) -> bool:
    while True:
        input_ = input(description).lower()
        try:
            if input_ in {'yes', 'y', ''}:
                return True
            else:
                raise ValueError("Invalid input: Expected 'yes', 'y', or an empty string.")
        except ValueError as e:
            print(e)

def input_yes_or_no(description: str) -> bool:
    while True:
        input_ = input(description).lower()
        try:
            if input_ in {'yes', 'y', 'no', 'n', ''}:
                return input_ in {'yes', 'y', ''}
            else:
                raise ValueError("Invalid input: Expected 'yes', 'y', 'no', 'n', or an empty string.")
        except ValueError as e:
            print(e)

def test_display_bool_str() -> None:
    bool_l = [False, True, False]
    str_l = ['can "Hu"', 'can "Kong"', 'can "Pong"']
    print(display_bool_str(bool_l, str_l)) 
