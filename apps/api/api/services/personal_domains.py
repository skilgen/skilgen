from __future__ import annotations

PERSONAL_EMAIL_DOMAINS: set[str] = {
    "aol.com",
    "gmail.com",
    "hotmail.com",
    "icloud.com",
    "live.com",
    "me.com",
    "msn.com",
    "outlook.com",
    "proton.me",
    "protonmail.com",
    "yahoo.com",
}


def is_personal_domain(domain: str) -> bool:
    return domain.strip().lower() in PERSONAL_EMAIL_DOMAINS

