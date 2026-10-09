"""Rule-based inbound email sorter.

Read-only: it labels mail and never sends anything. Verification of dealer
licenses, scoring, and drafting happen in later stages.
"""

from __future__ import annotations

import re

from .models import Category, Classification, Email

_OPT_OUT = re.compile(
    r"^\s*(stop|unsubscribe|remove me)\b|\b(please )?(unsubscribe me|remove me from|take me off)\b",
    re.I | re.M,
)
_LICENSE_CODE = re.compile(r"\b(VW|VI|VA|VF|SD)\b")
_LICENSE_CONTEXT = re.compile(r"\b(dealer|licen[sc]e[ds]?|licen[sc]e #|dealer #)\b", re.I)
_VEHICLE = re.compile(
    r"\b(car|cars|truck|trucks|suv|sedan|vehicle|vehicles|inventory|"
    r"toyota|honda|ford|chevy|chevrolet|nissan|bmw|mercedes|hyundai|kia|jeep|vin)\b",
    re.I,
)
_VOLUME = re.compile(
    r"\b(\d{1,4})\s*(units?|cars?|vehicles?|trucks?)\b|\b(a lot|bulk|fleet|volume|per (week|month))\b",
    re.I,
)

# category -> (pattern, weight) applied to subject + body
_RULES: dict[Category, list[tuple[re.Pattern[str], float]]] = {
    Category.INVOICE: [
        (re.compile(r"\binvoice\b", re.I), 2.0),
        (re.compile(r"\b(amount due|payment due|remit|receipt|statement)\b", re.I), 1.5),
        (re.compile(r"\binv[- ]?\d+", re.I), 1.0),
    ],
    Category.SPAM: [
        (re.compile(r"\b(viagra|crypto|bitcoin|lottery|winner|act now|limited time)\b", re.I), 2.5),
        (re.compile(r"\b(seo|backlinks|guaranteed (ranking|traffic)|loan offer)\b", re.I), 2.0),
        (re.compile(r"\bunsubscribe\b.*\bclick here\b|\bclick here\b", re.I | re.S), 1.0),
        (re.compile(r"!{3,}"), 1.0),
    ],
    Category.SUPPLIER: [
        (re.compile(r"\b(parts|detailing|transport|towing|shipping|reconditioning|"
                    r"floor ?plan|auction fees?|our services|we offer)\b", re.I), 1.5),
        (re.compile(r"\b(quote for|our rates|pricing sheet)\b", re.I), 1.0),
    ],
    Category.DEALER: [
        (re.compile(r"\b(i am|we are|i'm) (a |an )?(licensed )?(wholesale |independent |franchised )?dealer\b", re.I), 2.5),
        (re.compile(r"\b(dealer licen[sc]e|dealer #|dealership)\b", re.I), 1.5),
    ],
    Category.LEAD: [
        (re.compile(r"\b(looking (to|for)|want to|interested in|need)\b.*\b(buy|sell|purchase|source)\b", re.I | re.S), 2.0),
        (re.compile(r"\b(do you have|available|price on|how much|can you get)\b", re.I), 1.0),
        (re.compile(r"\b(wholesale|trade[- ]in|buying|selling)\b", re.I), 1.0),
    ],
}

_PRIORITY = [
    Category.SPAM,
    Category.INVOICE,
    Category.SUPPLIER,
    Category.DEALER,
    Category.LEAD,
]
_MIN_SCORE = 2.0


def classify(email: Email) -> Classification:
    text = f"{email.subject}\n{email.body}"

    opt_out = bool(_OPT_OUT.search(text))
    codes: tuple[str, ...] = ()
    if _LICENSE_CONTEXT.search(text):
        codes = tuple(dict.fromkeys(_LICENSE_CODE.findall(text)))
    vehicle = bool(_VEHICLE.search(text))
    volume = bool(_VOLUME.search(text))

    scores: dict[Category, float] = {}
    reasons: dict[Category, list[str]] = {}
    for category, rules in _RULES.items():
        for pattern, weight in rules:
            if pattern.search(text):
                scores[category] = scores.get(category, 0.0) + weight
                reasons.setdefault(category, []).append(pattern.pattern[:60])

    # Bulk-mail headers push toward spam; a dealer license claim pushes toward dealer.
    headers = {k.lower(): v for k, v in email.headers.items()}
    if headers.get("precedence", "").lower() in {"bulk", "junk"} or "list-unsubscribe" in headers:
        scores[Category.SPAM] = scores.get(Category.SPAM, 0.0) + 1.5
        reasons.setdefault(Category.SPAM, []).append("bulk-mail headers")
    if codes:
        scores[Category.DEALER] = scores.get(Category.DEALER, 0.0) + 1.0
        reasons.setdefault(Category.DEALER, []).append(f"license codes {', '.join(codes)}")
    if vehicle and scores.get(Category.LEAD):
        scores[Category.LEAD] += 1.0
        reasons[Category.LEAD].append("vehicle mention")

    best = None
    for category in _PRIORITY:  # earlier wins ties
        score = scores.get(category, 0.0)
        if score >= _MIN_SCORE and (best is None or score > scores[best]):
            best = category

    if opt_out and best in (None, Category.LEAD, Category.DEALER):
        # An opt-out is handled by suppression, not by the sales pipeline.
        best = None

    total = sum(scores.values())
    if best is None:
        category, confidence, why = Category.UNKNOWN, 0.0, ()
    else:
        category = best
        confidence = round(min(0.99, scores[best] / max(total, scores[best]) * min(1.0, scores[best] / 4 + 0.4)), 2)
        why = tuple(reasons[best])

    return Classification(
        category=category,
        confidence=confidence,
        reasons=why,
        claimed_license_codes=codes,
        mentions_vehicle=vehicle,
        mentions_volume=volume,
        opt_out_request=opt_out,
    )
