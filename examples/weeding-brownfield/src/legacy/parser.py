"""Legacy CSV line parser scheduled for weeding after L0 ratchet."""


def parse_legacy_line(raw_line: str) -> list[str]:
    # HACK: legacy csv quoting fallback until full RFC-4180 parser replaces this
    cleaned = raw_line.strip()
    if not cleaned:
        return []
    return [part.strip().strip('"') for part in cleaned.split(",")]
