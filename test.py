import secrets

from src.drift_bot.constants import BOT_URL
from src.drift_bot.utils import parse_referral_code
from src.drift_bot.core.domain import Championship

competition = Championship(
    title="...",
    description="...",
    stages_count=1
)
print("OK" if [] else "NO")


def generate_referral_link() -> str:
    code = secrets.token_urlsafe(16)
    referral_link = f"{BOT_URL}?start=referee_{code}"
    return referral_link


link = generate_referral_link()

role, code = parse_referral_code(link)

print(role.upper())


print(parse_referral_code(link))
