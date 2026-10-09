"""Reply drafting. Produces drafts that wait for a person; nothing here sends.

A draft moves pending_approval -> approved | rejected. Approval re-checks the
suppression list, so a sender who opts out after the draft was written can
never be approved. The mail layer (not built yet) may only send drafts whose
status is `approved`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .licenses import Status, Verification
from .models import Classification, Email
from .scoring import Action, Score
from .suppression import SuppressionList, normalize_address


class DraftStatus(str, Enum):
    PENDING = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Business:
    """Who we are. The postal address is required on commercial email."""

    name: str
    sender_name: str
    postal_address: str
    phone: str = ""


@dataclass(frozen=True)
class Draft:
    to: str
    subject: str
    body: str
    status: DraftStatus
    needs_review: bool
    score: int
    notes: tuple[str, ...] = ()


class DraftError(Exception):
    pass


def _first_name(sender: str) -> str:
    name = sender.split("<")[0].strip().strip('"')
    return name.split()[0].title() if name and "@" not in name else ""


def _reply_subject(subject: str) -> str:
    return subject if subject.lower().startswith("re:") else f"Re: {subject}"


def _footer(biz: Business) -> str:
    lines = [biz.name, biz.postal_address]
    if biz.phone:
        lines.append(biz.phone)
    lines += ["", 'If you would rather not hear from us, reply "STOP" and we will remove you right away.']
    return "\n".join(lines)


def draft_reply(
    email: Email,
    classification: Classification,
    verification: Verification,
    result: Score,
    business: Business,
    suppression: SuppressionList,
) -> Draft | None:
    """Return a pending draft, or None when no reply should be written."""
    if result.action is Action.IGNORE:
        return None
    if not suppression.can_contact(email.sender):
        return None

    greeting = f"Hello {_first_name(email.sender)}," if _first_name(email.sender) else "Hello,"
    notes: list[str] = []
    verified = verification.status is Status.VERIFIED

    paragraphs = [greeting, f"Thank you for reaching out to {business.name}."]
    if classification.mentions_vehicle:
        paragraphs.append("We have received your note about the vehicles you are looking for and would be glad to help.")
    else:
        paragraphs.append("We would be glad to help with your wholesale needs.")

    if verified:
        notes.append(f"license {verification.record.license_number} verified")
        paragraphs.append(
            "To make sure we match you with the right inventory, could you tell us the makes, models and "
            "quantities you are after, and your preferred timing?"
        )
    else:
        notes.append("license not confirmed; draft asks for it")
        paragraphs.append(
            "As we trade only with licensed dealers, could you please send your Florida dealer license "
            "number? Once we have it, we will follow up with details on current inventory."
        )

    paragraphs.append(f"Kind regards,\n{business.sender_name}")
    body = "\n\n".join(paragraphs) + "\n\n--\n" + _footer(business)

    return Draft(
        to=normalize_address(email.sender),
        subject=_reply_subject(email.subject),
        body=body,
        status=DraftStatus.PENDING,
        needs_review=not verified or result.action is Action.REVIEW,
        score=result.value,
        notes=tuple(notes),
    )


def edit(draft: Draft, *, subject: str | None = None, body: str | None = None) -> Draft:
    if draft.status is not DraftStatus.PENDING:
        raise DraftError("only pending drafts can be edited")
    return replace(draft, subject=subject if subject is not None else draft.subject,
                   body=body if body is not None else draft.body)


def approve(draft: Draft, suppression: SuppressionList) -> Draft:
    if draft.status is not DraftStatus.PENDING:
        raise DraftError(f"draft is already {draft.status.value}")
    if not suppression.can_contact(draft.to):
        raise DraftError("recipient is on the suppression list")
    if "STOP" not in draft.body:
        raise DraftError("draft is missing the opt-out line")
    return replace(draft, status=DraftStatus.APPROVED)


def reject(draft: Draft) -> Draft:
    if draft.status is not DraftStatus.PENDING:
        raise DraftError(f"draft is already {draft.status.value}")
    return replace(draft, status=DraftStatus.REJECTED)
