"""Parse PGST panel DP26 message payloads."""
import re

_ZONE_RE = re.compile(r"(?im)^\s*Zone\s*:\s*0*(\d{1,3})(?!\d)")


def parse_zone(message: str | None) -> str | None:
    """Return canonical three-digit zone ID; ignore invalid messages."""
    if not isinstance(message, str):
        return None
    match = _ZONE_RE.search(message)
    if not match:
        return None
    number = int(match.group(1))
    return f"{number:03d}" if 0 <= number <= 255 else None
