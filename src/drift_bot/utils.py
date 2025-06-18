

def parse_referral_link(referral_link: str) -> tuple[str, str]:
    start_part = referral_link.split("start=")[1]
    referee, code = start_part.split("_", 1)
    return referee.upper(), code
