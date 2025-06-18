import secrets

from src.drift_bot.constants import BOT_URL
from src.drift_bot.utils import parse_referral_link


def generate_referral_link() -> str:
    code = secrets.token_urlsafe(16)
    referral_link = f"{BOT_URL}?start=referee_{code}"
    return referral_link


link = generate_referral_link()

role, code = parse_referral_link(link)

print(role.upper())
