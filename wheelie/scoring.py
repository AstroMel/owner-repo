"""Lead scoring: turns the sorter and license results into a 0-100 score,
a tier, and a next action. Scoring never sends anything; DRAFT means "a reply
may be drafted for human approval".

Weights follow docs/PROJECT.md: the license is the strongest signal, then a
named vehicle or volume, then a real (non-residential) office address.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .licenses import Status, Verification
from .models import Category, Classification, Email
from .suppression import SuppressionList

POINTS_VERIFIED = 50
POINTS_REVIEW = 20
POINTS_VEHICLE = 15
POINTS_VOLUME = 15
POINTS_INTENT = 5
POINTS_OFFICE = 10
PENALTY_NOT_AN_OFFICE = 10

HOT_MIN = 70
WARM_MIN = 40

# Caps applied when the license evidence is bad or the license type is not a buyer.
CAP_AUCTION = 45
CAP_NOT_FOUND = 25
CAP_INELIGIBLE = 30
CAP_INACTIVE = 20

_NOT_AN_OFFICE = re.compile(r"\b(p\.?\s?o\.?\s*box|apt\.?|apartment|mailbox|pmb)\b|\bunit\s*#", re.I)


class Tier(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    DROP = "drop"  # not a lead at all, or must not be contacted


class Action(str, Enum):
    DRAFT = "draft"  # draft a reply for human approval
    REVIEW = "review"  # a person looks first
    IGNORE = "ignore"


@dataclass(frozen=True)
class Score:
    value: int
    tier: Tier
    action: Action
    reasons: tuple[str, ...]


def looks_like_non_office(address: str) -> bool:
    """Heuristic only: PO boxes, mailbox stores and apartments are not a statutory office.
    Real office checking needs a second source and is still open in docs/PROJECT.md."""
    return bool(_NOT_AN_OFFICE.search(address))


def _drop(reason: str) -> Score:
    return Score(0, Tier.DROP, Action.IGNORE, (reason,))


def score(
    email: Email,
    classification: Classification,
    verification: Verification,
    suppression: SuppressionList | None = None,
) -> Score:
    # Gates: nothing below can rescue these.
    if classification.opt_out_request:
        return _drop("sender asked to stop")
    if suppression is not None and not suppression.can_contact(email.sender):
        return _drop("sender is on the suppression list")
    if classification.category not in (Category.LEAD, Category.DEALER):
        return _drop(f"classified as {classification.category.value}, not a lead")

    points = 0
    reasons: list[str] = []
    cap = 100

    def add(p: int, why: str) -> None:
        nonlocal points
        points += p
        reasons.append(f"{p:+d} {why}")

    status = verification.status
    record = verification.record
    if status is Status.VERIFIED:
        add(POINTS_VERIFIED, f"verified {record.license_type} license")
        if record.license_type == "VA":
            cap = CAP_AUCTION
            reasons.append(f"cap {CAP_AUCTION}: auction dealers are a channel, not a buyer")
    elif status is Status.REVIEW:
        add(POINTS_REVIEW, "partial license match, needs a person to confirm")
    elif status is Status.NOT_FOUND:
        cap = CAP_NOT_FOUND
        reasons.append(f"cap {CAP_NOT_FOUND}: claimed license is not in the registry")
    elif status is Status.INELIGIBLE_TYPE:
        cap = CAP_INELIGIBLE
        reasons.append(f"cap {CAP_INELIGIBLE}: license type {record.license_type} is not a wholesale buyer")
    elif status is Status.INACTIVE:
        cap = CAP_INACTIVE
        reasons.append(f"cap {CAP_INACTIVE}: license is not active")
    else:
        reasons.append("no license claim")

    if classification.mentions_vehicle:
        add(POINTS_VEHICLE, "names a vehicle")
    if classification.mentions_volume:
        add(POINTS_VOLUME, "mentions volume")
    add(POINTS_INTENT, f"classified as {classification.category.value}")

    if record is not None and status in (Status.VERIFIED, Status.REVIEW) and record.address:
        if looks_like_non_office(record.address):
            add(-PENALTY_NOT_AN_OFFICE, "registered address looks like a PO box or apartment")
        else:
            add(POINTS_OFFICE, "registered address looks like a real office")

    value = max(0, min(points, cap, 100))
    if value >= HOT_MIN:
        tier = Tier.HOT
    elif value >= WARM_MIN:
        tier = Tier.WARM
    else:
        tier = Tier.COLD

    if tier is Tier.HOT and status is Status.VERIFIED:
        action = Action.DRAFT
    elif tier is Tier.COLD:
        action = Action.IGNORE
    else:
        action = Action.REVIEW
    return Score(value, tier, action, tuple(reasons))
