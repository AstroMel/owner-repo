"""Dealer license verification against a state dealer records file.

The registry is loaded from CSV (the state list filtered to Orange County once
we have it). Columns: license_number, business_name, license_type, status,
county, address, domain. `domain` is optional.

Assumption to confirm against the real state file: license numbers are compared
after stripping spaces/dashes and upper-casing, so "VI 12345" == "vi-12345".
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .models import Email

ELIGIBLE_TYPES = frozenset({"VW", "VI", "VA"})  # direct fit, strong fit, auction channel
_FREE_MAIL = frozenset({"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com"})
_NUMBER_CLAIM = re.compile(
    r"\b(?:dealer\s+)?(?:licen[sc]e|lic)\s*(?:#|no\.?|number)?\s*(?:is\b|was\b|[:#])?\s*[:#]?\s*([A-Za-z]{0,2}[ -]?\d{4,8})\b",
    re.I,
)


def normalize_license(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def normalize_name(value: str) -> str:
    value = re.sub(r"\b(llc|inc|corp|co|ltd)\b\.?", "", value.lower())
    return re.sub(r"[^a-z0-9]", "", value)


class Status(str, Enum):
    VERIFIED = "verified"
    REVIEW = "review"  # partial match; a human decides
    INACTIVE = "inactive"
    INELIGIBLE_TYPE = "ineligible_type"
    NOT_FOUND = "not_found"
    NO_CLAIM = "no_claim"


@dataclass(frozen=True)
class DealerRecord:
    license_number: str
    business_name: str
    license_type: str
    status: str
    county: str = ""
    address: str = ""
    domain: str = ""

    @property
    def active(self) -> bool:
        return self.status.strip().lower() in {"active", "current"}


@dataclass(frozen=True)
class Verification:
    status: Status
    record: DealerRecord | None = None
    reasons: tuple[str, ...] = ()

    @property
    def passes_filter(self) -> bool:
        """True only for a clean match; everything else needs a human or is dropped."""
        return self.status is Status.VERIFIED


class DealerRegistry:
    def __init__(self, records: list[DealerRecord]):
        self._by_number = {normalize_license(r.license_number): r for r in records}
        self._by_domain: dict[str, list[DealerRecord]] = {}
        self._by_name: dict[str, list[DealerRecord]] = {}
        for r in records:
            if r.domain:
                self._by_domain.setdefault(r.domain.lower(), []).append(r)
            self._by_name.setdefault(normalize_name(r.business_name), []).append(r)

    @classmethod
    def from_csv(cls, path: str | Path) -> "DealerRegistry":
        with open(path, newline="", encoding="utf-8") as f:
            rows = [
                DealerRecord(
                    license_number=(row.get("license_number") or "").strip(),
                    business_name=(row.get("business_name") or "").strip(),
                    license_type=(row.get("license_type") or "").strip().upper(),
                    status=(row.get("status") or "").strip(),
                    county=(row.get("county") or "").strip(),
                    address=(row.get("address") or "").strip(),
                    domain=(row.get("domain") or "").strip().lower(),
                )
                for row in csv.DictReader(f)
            ]
        return cls([r for r in rows if r.license_number])

    def __len__(self) -> int:
        return len(self._by_number)

    def by_number(self, number: str) -> DealerRecord | None:
        return self._by_number.get(normalize_license(number))

    def by_domain(self, domain: str) -> list[DealerRecord]:
        return self._by_domain.get(domain.lower(), [])

    def by_name(self, name: str) -> list[DealerRecord]:
        return self._by_name.get(normalize_name(name), [])

    def find_names_in(self, text: str) -> list[DealerRecord]:
        """Records whose business name appears in `text` (normalized)."""
        haystack = normalize_name(text)
        return [rs[0] for key, rs in self._by_name.items() if key and key in haystack]


def sender_domain(sender: str) -> str:
    m = re.search(r"@([A-Za-z0-9.-]+)", sender)
    return m.group(1).lower() if m else ""


def extract_license_numbers(text: str) -> list[str]:
    seen: dict[str, str] = {}
    for m in _NUMBER_CLAIM.finditer(text):
        seen.setdefault(normalize_license(m.group(1)), m.group(1).strip())
    return list(seen.values())


def verify(email: Email, registry: DealerRegistry) -> Verification:
    text = f"{email.subject}\n{email.body}"
    domain = sender_domain(email.sender)
    own_domain = domain and domain not in _FREE_MAIL

    numbers = extract_license_numbers(text)
    if numbers:
        for number in numbers:
            record = registry.by_number(number)
            if record is None:
                continue
            return _judge_number_match(record, domain, own_domain)
        return Verification(Status.NOT_FOUND, None, (f"license {numbers[0]} not in registry",))

    # No license number given: a domain or name match is a hint, never a pass.
    if own_domain:
        hits = registry.by_domain(domain)
        if hits:
            return Verification(
                Status.REVIEW, hits[0], (f"sender domain {domain} matches {hits[0].business_name}; no license number given",)
            )
    named = registry.find_names_in(text)
    if named:
        hit = named[0]
        return Verification(Status.REVIEW, hit, (f"business name '{hit.business_name}' mentioned; no license number given",))
    return Verification(Status.NO_CLAIM, None, ("no license number, matching domain, or business name",))


def _judge_number_match(record: DealerRecord, domain: str, own_domain: bool) -> Verification:
    reasons = [f"license {record.license_number} matches {record.business_name}"]
    if not record.active:
        return Verification(Status.INACTIVE, record, (*reasons, f"status is {record.status}"))
    if record.license_type not in ELIGIBLE_TYPES:
        return Verification(Status.INELIGIBLE_TYPE, record, (*reasons, f"type {record.license_type} is not VW/VI/VA"))
    if record.domain and own_domain and domain != record.domain:
        return Verification(
            Status.REVIEW, record, (*reasons, f"sender domain {domain} differs from registered {record.domain}")
        )
    if record.domain and not own_domain:
        return Verification(Status.REVIEW, record, (*reasons, "sender uses a free-mail address; cannot confirm identity"))
    reasons.append("active, eligible type")
    if record.domain:
        reasons.append("sender domain matches")
    return Verification(Status.VERIFIED, record, tuple(reasons))
