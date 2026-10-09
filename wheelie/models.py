from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    LEAD = "lead"
    DEALER = "dealer"
    SUPPLIER = "supplier"
    INVOICE = "invoice"
    SPAM = "spam"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Email:
    sender: str
    subject: str
    body: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Classification:
    category: Category
    confidence: float
    reasons: tuple[str, ...] = ()
    # Florida dealer license codes the sender claims (VW, VI, VA...). Claims only:
    # they still have to be verified against state records downstream.
    claimed_license_codes: tuple[str, ...] = ()
    mentions_vehicle: bool = False
    mentions_volume: bool = False
    # Sender asked to stop (unsubscribe/STOP). Must feed the suppression list
    # the same day and never get a drafted reply.
    opt_out_request: bool = False
