

def parse_referral_code(url: str) -> str:
    """Парсит реферальный код из стартовой ссылки."""
    parts = url.split("start=")
    return parts[-1] if len(parts) > 1 else ""
