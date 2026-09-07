"""Random sovg'a — kriptografik tasodifiy tanlov + shaffoflik xeshi."""
import hashlib
import secrets


def candidates_hash(user_ids: list[int]) -> str:
    """Nomzodlar ro'yxatining sha256 qisqa xeshi — o'ynalgandan keyin
    ro'yxat o'zgarmaganini isbotlash uchun."""
    ordered = ",".join(str(i) for i in sorted(user_ids))
    return hashlib.sha256(ordered.encode()).hexdigest()[:12]


def pick_winners(user_ids: list[int], n: int, rand=None) -> list[int]:
    """SystemRandom (OS CSPRNG) bilan n ta g'olib tanlaydi."""
    if rand is None:
        rand = secrets.SystemRandom()
    ids = sorted(user_ids)
    n = min(n, len(ids))
    if n <= 0:
        return []
    return rand.sample(ids, n)
