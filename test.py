import secrets

from src.drift_bot.constants import BOT_URL


def generate_referral_link() -> str:
    code = secrets.token_urlsafe(16)
    referral_link = f"{BOT_URL}?start=referee_{code}"
    return referral_link


print(generate_referral_link())
