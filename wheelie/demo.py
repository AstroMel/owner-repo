"""Builds the sample queue the approval UI shows (made-up emails and dealers).

    python3 -m wheelie.demo            # writes ui/queue.js
"""

from __future__ import annotations

import json
from pathlib import Path

from . import DealerRegistry, Email, SuppressionList, classify, score, verify
from .drafting import Business, draft_reply

ROOT = Path(__file__).resolve().parent.parent
BUSINESS = Business("Wheelie Wholesale", "Alex Morgan", "100 Sample Street, Orlando, FL 32801", "(407) 555-0100")

SAMPLES = [
    Email("Dana Whitfield <dana@sunshinewholesale.example>", "Wholesale SUVs for our lot",
          "Hello, we are looking to buy 20 SUVs this month, mostly Toyota and Honda. Our dealer license is VW12345. Do you have any available?"),
    Email("Marcus Bell <marcus@palmmotors.example>", "Interested in your trucks",
          "I want to buy 30 trucks over the next quarter. Do you have any available? Palm Motors."),
    Email("Priya Nair <priya.nair@gmail.com>", "Sedans for resale",
          "Looking for 8 sedans per month for resale. Dealer license VI55555."),
    Email("Tom Hargrove <tom@oldlot.example>", "Buying cars",
          "I want to buy 50 cars. Dealer license VW44444. Do you have any available?"),
    Email("Lena Ortiz <lena@citrusford.example>", "Fleet vehicles",
          "We want to buy a fleet of vehicles. License VF33333. Do you have any available?"),
    Email("billing@towco.example", "Invoice INV-2041", "Invoice attached. Amount due within 30 days, please remit."),
    Email("deals@promo.example", "WINNER!!!", "Act now, guaranteed traffic. Click here!!!", {"List-Unsubscribe": "<x>"}),
    Email("Rae Collins <rae@example.org>", "Re: Wholesale SUVs", "STOP"),
]


def build() -> list[dict]:
    registry = DealerRegistry.from_csv(ROOT / "tests" / "data" / "dealers_sample.csv")
    suppression = SuppressionList()
    queue = []
    for i, mail in enumerate(SAMPLES, 1):
        c, v = classify(mail), verify(mail, registry)
        if c.opt_out_request:
            from .suppression import record_opt_out
            record_opt_out(mail, c, suppression)
        s = score(mail, c, v, suppression)
        d = draft_reply(mail, c, v, s, BUSINESS, suppression)
        queue.append({
            "id": i,
            "sender": mail.sender,
            "subject": mail.subject,
            "excerpt": mail.body[:220],
            "category": c.category.value,
            "optOut": c.opt_out_request,
            "score": s.value,
            "tier": s.tier.value,
            "action": s.action.value,
            "reasons": list(s.reasons),
            "license": {
                "status": v.status.value,
                "business": v.record.business_name if v.record else None,
                "type": v.record.license_type if v.record else None,
                "number": v.record.license_number if v.record else None,
                "notes": list(v.reasons),
            },
            "draft": None if d is None else {
                "to": d.to, "subject": d.subject, "body": d.body, "needsReview": d.needs_review,
            },
        })
    return queue


def main() -> None:
    out = ROOT / "ui" / "queue.js"
    out.write_text("window.WHEELIE_QUEUE = " + json.dumps(build(), indent=2) + ";\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
