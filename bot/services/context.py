"""Menyu holatini hisoblash uchun umumiy yordamchi."""
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import ExpoStatus, SubStatus
from ..db import repo
from ..db.models import Expo, Participant, Submission, User, utcnow


class Ctx:
    def __init__(self, expo, participant, submission, is_admin):
        self.expo: Expo | None = expo
        self.participant: Participant | None = participant
        self.submission: Submission | None = submission
        self.is_admin = is_admin

    @property
    def expo_open(self) -> bool:
        return (self.expo is not None
                and self.expo.status == ExpoStatus.ACTIVE
                and self.expo.start_at <= utcnow() <= self.expo.end_at)

    @property
    def can_join(self) -> bool:
        return self.expo is not None and self.expo.status == ExpoStatus.ACTIVE \
            and self.participant is None

    @property
    def can_send(self) -> bool:
        if not self.expo_open or self.participant is None:
            return False
        if self.submission is None:
            return True
        return self.submission.status in (SubStatus.REJECTED, SubStatus.CHANGES)

    @property
    def can_update(self) -> bool:
        if self.participant is None or self.submission is None:
            return False
        if self.submission.status != SubStatus.APPROVED:
            return False
        # update mumkin: faol davrda yoki yakundan keyin final tekshiruv oynasida
        if self.expo and self.expo.status == ExpoStatus.ACTIVE and self.expo_open:
            return True
        return self.expo is not None and self.expo.status == ExpoStatus.FINISHED


async def build_ctx(session: AsyncSession, user: User | None, role: str | None) -> Ctx:
    expo = await repo.get_active_expo(session)
    participant = submission = None
    if expo and user:
        participant = await repo.get_participant(session, user.id, expo.id)
        if participant:
            submission = await repo.get_submission_for_participant(session, participant.id)
    # yakunlangan expo ham reyting uchun kerak bo'lishi mumkin — lekin aktivga e'tibor
    if expo is None and user:
        finished = (await repo.list_expos(session, limit=1))
        if finished and finished[0].status in (ExpoStatus.FINISHED, ExpoStatus.CLOSED):
            expo = finished[0]
            participant = await repo.get_participant(session, user.id, expo.id)
            if participant:
                submission = await repo.get_submission_for_participant(session, participant.id)
    from ..constants import Role
    return Ctx(expo, participant, submission, role in (Role.ADMIN, Role.SUPERADMIN))
