"""Servis qatlamining sof funksiyalari uchun testlar."""
from datetime import datetime, timedelta

from bot.services.flags import (FLAG_JUMP, FLAG_NEGATIVE, compute_flags)
from bot.services.random_draw import candidates_hash, pick_winners
from bot.services.ranking import find_rank
from bot.services.utils import (fmt_dt, is_reels_link, mask_handle,
                                normalize_insta, parse_date, parse_views,
                                tash_to_utc, utc_to_tash)


class Obj:
    def __init__(self, id, views):
        self.id = id
        self.current_views = views


class TestUtils:
    def test_parse_views(self):
        assert parse_views("12 500") == 12500
        assert parse_views("12,500") == 12500
        assert parse_views("  12500 ") == 12500
        assert parse_views("abc") is None

    def test_reels_link(self):
        assert is_reels_link("https://www.instagram.com/reel/C1abcDEF23/")
        assert is_reels_link("https://instagram.com/reels/XYZ12345")
        assert not is_reels_link("https://youtu.be/xyz")
        assert not is_reels_link("instagram.com/reel/abc")  # https shart

    def test_insta(self):
        assert normalize_insta("@Ali_Sher.09") == "ali_sher.09"
        assert normalize_insta("bad name!") is None

    def test_mask(self):
        assert mask_handle("alisher_nur") == "@alis***"
        assert mask_handle(None) == "—"

    def test_parse_date(self):
        assert parse_date("01.10.2026 10:00") == datetime(2026, 10, 1, 10, 0)
        assert parse_date("01.10.2026") is not None
        assert parse_date("bugun") is None


class TestFlags:
    def test_negative(self):
        now = datetime(2026, 9, 7, 12, 0)
        prev = now - timedelta(minutes=10)
        flags = compute_flags(5000, 4000, prev, now)
        assert flags == [FLAG_NEGATIVE]

    def test_jump(self):
        now = datetime(2026, 9, 7, 12, 0)
        prev = now - timedelta(minutes=30)
        flags = compute_flags(1000, 1000 + 5000, prev, now, 30, 5000)
        assert FLAG_JUMP in flags

    def test_normal_growth_no_flags(self):
        now = datetime(2026, 9, 7, 12, 0)
        prev = now - timedelta(days=1)
        flags = compute_flags(10000, 12000, prev, now, 30, 5000)
        assert flags == []

    def test_first_report(self):
        flags = compute_flags(None, 50000, None, datetime(2026, 9, 7))
        assert flags == []


class TestRanking:
    def test_rank(self):
        rows = [Obj(1, 500), Obj(2, 300), Obj(3, 100)]
        rank, total, idx = find_rank(rows, 2, views_key=lambda r: r.current_views)
        assert (rank, total, idx) == (2, 3, 1)


class TestRandomDraw:
    def test_pick_winners_deterministic(self):
        import random
        ids = [5, 1, 9, 3, 7]
        w = pick_winners(ids, 2, rand=random.Random(42))
        assert len(w) == 2
        assert set(w) <= set(ids)
        # bir xil seed = bir xil natija (takrorlanuvchanlik → tekshirish mumkin)
        assert w == pick_winners(ids, 2, rand=random.Random(42))

    def test_pick_more_than_candidates(self):
        ids = [1, 2, 3]
        w = pick_winners(ids, 10, rand=__import__("random").Random(1))
        assert sorted(w) == [1, 2, 3]  # n > nomzodlar → hammasi olinadi

    def test_empty(self):
        assert pick_winners([], 3) == []

    def test_hash_stable(self):
        assert candidates_hash([3, 1, 2]) == candidates_hash([1, 2, 3])
        assert candidates_hash([1, 2, 3]) != candidates_hash([1, 2, 4])
        assert len(candidates_hash([1, 2, 3])) == 12


class TestTimezone:
    def test_roundtrip(self):
        u = datetime(2026, 9, 7, 10, 0)
        assert utc_to_tash(tash_to_utc(u)) == u

    def test_fmt_dt_shows_tashkent(self):
        # 10:00 UTC → Toshkentda 15:00
        assert fmt_dt(datetime(2026, 9, 7, 10, 0)) == "07.09.2026 15:00"
