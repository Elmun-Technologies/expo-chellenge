"""Servis qatlamining sof funksiyalari uchun testlar."""
from datetime import datetime, timedelta

from bot.services.flags import (FLAG_JUMP, FLAG_NEGATIVE, compute_flags)
from bot.services.ranking import find_rank
from bot.services.utils import (is_reels_link, mask_handle, normalize_insta,
                                parse_date, parse_views)


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
