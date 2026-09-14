"""Skrinshot OCR uchun parslash va flag funksiyalari testlari."""
from bot.services.flags import (FLAG_ACCOUNT_MISMATCH, FLAG_OCR_MISMATCH,
                                ocr_flags)
from bot.services.utils import detect_handle, parse_views, parse_views_from_text


class TestParseViews:
    def test_plain(self):
        assert parse_views("12500") == 12500
        assert parse_views("  12500 ") == 12500

    def test_thousands_separators(self):
        assert parse_views("12 500") == 12500
        assert parse_views("12,500") == 12500
        assert parse_views("12.500") == 12500
        assert parse_views("1 250 500") == 1250500

    def test_k_suffix(self):
        assert parse_views("12,5K") == 12500
        assert parse_views("12.5K") == 12500
        assert parse_views("12,5 ming") == 12500
        assert parse_views("12,5 минг") == 12500
        assert parse_views("12.5 тыс.") == 12500

    def test_m_suffix(self):
        assert parse_views("1,2M") == 1_200_000
        assert parse_views("1.2M") == 1_200_000
        assert parse_views("1,2 млн") == 1_200_000

    def test_invalid(self):
        assert parse_views("abc") is None
        assert parse_views("") is None
        assert parse_views(None) is None


class TestParseViewsFromText:
    def test_label_russian(self):
        assert parse_views_from_text("12 500 просмотров") == 12500

    def test_label_english(self):
        assert parse_views_from_text("1 234 views") == 1234

    def test_mixed_noise(self):
        text = "reels\n@alisher_nur\n12,5K\n3 200 likes\n240 comments"
        assert parse_views_from_text(text) == 12500

    def test_fallback_no_label(self):
        assert parse_views_from_text("12 500\n3 200") == 12500

    def test_empty(self):
        assert parse_views_from_text("") is None


class TestDetectHandle:
    def test_simple(self):
        assert detect_handle("@Ali_Sher.09") == "ali_sher.09"

    def test_known_preferred(self):
        text = "@other_user\n@alisher_nur reels"
        assert detect_handle(text, "alisher_nur") == "alisher_nur"

    def test_without_at(self):
        assert detect_handle("Video\nAli Sher\nalisher_nur", "alisher_nur") == "alisher_nur"

    def test_none(self):
        assert detect_handle("hello world") is None


class TestOcrFlags:
    def test_view_mismatch(self):
        flags = ocr_flags(10000, 12500, None, None)
        assert FLAG_OCR_MISMATCH in flags

    def test_view_match(self):
        assert ocr_flags(12500, 12500, None, None) == []

    def test_no_ocr(self):
        assert ocr_flags(10000, None, None, None) == []

    def test_account_mismatch(self):
        flags = ocr_flags(10000, 10000, "alisher_nur", "boshqa_user")
        assert FLAG_ACCOUNT_MISMATCH in flags

    def test_account_match(self):
        assert ocr_flags(10000, 10000, "Alisher_Nur", "alisher_nur") == []
