"""Reyting hisoblash (tartiblangan ro'yxatdan o'rin va qo'shnilar)."""
from typing import Sequence, TypeVar

T = TypeVar("T")

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def medal(place: int) -> str:
    return MEDALS.get(place, f"{place}.")


def find_rank(ordered: Sequence, target_id: int, views_key, id_key=lambda x: x.id):
    """
    ordered: current_views bo'yicha DESC tartiblangan obyektlar.
    Qaytaradi: (rank_1based, total, index) yoki None.
    """
    for i, item in enumerate(ordered):
        if id_key(item) == target_id:
            return i + 1, len(ordered), i
    return None


def neighbors(ordered: Sequence, index: int, views_key):
    """(yuqoridagi, pastdagi) elementlar yoki None."""
    above = ordered[index - 1] if index > 0 else None
    below = ordered[index + 1] if index + 1 < len(ordered) else None
    return above, below
