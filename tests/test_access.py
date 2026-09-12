"""Hay'at guruhi a'zoligiga ko'ra review huquqi testlari."""
from types import SimpleNamespace

import pytest
from aiogram.exceptions import TelegramBadRequest

from bot.constants import Role
from bot.services import access

REVIEW_CHAT = -100123


class FakeMember:
    def __init__(self, status, is_member=None):
        self.status = status
        if is_member is not None:
            self.is_member = is_member


class FakeBot:
    """get_chat_member ni taqlid qiluvchi bot."""

    def __init__(self, members=None, exc=None):
        self.members = members or {}
        self.exc = exc
        self.calls = 0

    async def get_chat_member(self, chat_id, user_id):
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        return self.members.get(user_id, FakeMember("left"))


@pytest.fixture(autouse=True)
def _clear_cache():
    access._cache.clear()
    yield
    access._cache.clear()


@pytest.fixture
def review_settings(monkeypatch):
    monkeypatch.setattr(
        access, "get_settings",
        lambda: SimpleNamespace(review_group_id=REVIEW_CHAT),
    )


class TestIsMemberStatus:
    def test_active_statuses(self):
        assert access.is_member_status("creator")
        assert access.is_member_status("administrator")
        assert access.is_member_status("member")

    def test_left_and_kicked(self):
        assert not access.is_member_status("left")
        assert not access.is_member_status("kicked")

    def test_restricted(self):
        assert access.is_member_status("restricted", is_member=True)
        assert not access.is_member_status("restricted", is_member=False)


class TestIsChatMember:
    pytestmark = pytest.mark.asyncio

    async def test_member_allowed(self):
        bot = FakeBot({10: FakeMember("member")})
        assert await access.is_chat_member(bot, REVIEW_CHAT, 10)

    async def test_left_denied(self):
        bot = FakeBot({10: FakeMember("left")})
        assert not await access.is_chat_member(bot, REVIEW_CHAT, 10)

    async def test_never_been_in_chat_denied(self):
        bot = FakeBot(exc=TelegramBadRequest(method=None, message="user not found"))
        assert not await access.is_chat_member(bot, REVIEW_CHAT, 77)

    async def test_cached_one_api_call(self):
        bot = FakeBot({10: FakeMember("administrator")})
        assert await access.is_chat_member(bot, REVIEW_CHAT, 10)
        assert await access.is_chat_member(bot, REVIEW_CHAT, 10)
        assert bot.calls == 1

    async def test_anonymous_admin_bypasses_api(self):
        bot = FakeBot()  # bo'sh — chaqirilsa "left" qaytadi
        assert await access.is_chat_member(
            bot, REVIEW_CHAT, access.GROUP_ANONYMOUS_BOT_ID)
        assert bot.calls == 0

    async def test_no_ids(self):
        assert not await access.is_chat_member(FakeBot(), None, 1)
        assert not await access.is_chat_member(FakeBot(), REVIEW_CHAT, None)


class TestCanReview:
    pytestmark = pytest.mark.asyncio

    @pytest.mark.usefixtures("review_settings")
    async def test_db_role_always_allowed(self):
        # guruhda bo'lmasa ham bazadagi moderator huquqi saqlanadi
        bot = FakeBot()
        for role in Role.REVIEWERS:
            assert await access.can_review(bot, role, REVIEW_CHAT, 55)
        assert bot.calls == 0

    @pytest.mark.usefixtures("review_settings")
    async def test_group_member_allowed(self):
        bot = FakeBot({20: FakeMember("member")})
        assert await access.can_review(bot, None, REVIEW_CHAT, 20)

    @pytest.mark.usefixtures("review_settings")
    async def test_non_member_denied(self):
        bot = FakeBot({20: FakeMember("kicked")})
        assert not await access.can_review(bot, None, REVIEW_CHAT, 20)

    @pytest.mark.usefixtures("review_settings")
    async def test_other_group_not_enough(self):
        # boshqa guruhdagi a'zolik review huquqini bermaydi
        bot = FakeBot({20: FakeMember("member")})
        assert not await access.can_review(bot, None, -100999, 20)

    async def test_no_review_group_configured(self, monkeypatch):
        monkeypatch.setattr(
            access, "get_settings",
            lambda: SimpleNamespace(review_group_id=None),
        )
        bot = FakeBot({20: FakeMember("creator")})
        assert not await access.can_review(bot, None, REVIEW_CHAT, 20)
