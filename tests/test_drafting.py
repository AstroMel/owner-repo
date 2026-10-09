import unittest
from pathlib import Path

from wheelie import DealerRegistry, Email, SuppressionList, classify, score, verify
from wheelie.drafting import Business, DraftError, DraftStatus, approve, draft_reply, edit, reject

REGISTRY = DealerRegistry.from_csv(Path(__file__).parent / "data" / "dealers_sample.csv")
BIZ = Business("Example Wholesale", "Sam Rivera", "1 Demo Plaza, Orlando, FL 32801")


def make(sender, body, subject="Looking to buy", supp=None):
    mail = Email(sender, subject, body)
    c, v = classify(mail), verify(mail, REGISTRY)
    supp = supp or SuppressionList()
    return draft_reply(mail, c, v, score(mail, c, v, supp), BIZ, supp), supp


HOT = "We are looking to buy 20 SUVs. Dealer license VW12345. Do you have any available?"


class DraftTests(unittest.TestCase):
    def test_hot_lead_gets_pending_draft(self):
        d, _ = make("Ana Cruz <buyer@sunshinewholesale.example>", HOT)
        self.assertEqual(d.status, DraftStatus.PENDING)
        self.assertEqual(d.to, "buyer@sunshinewholesale.example")
        self.assertEqual(d.subject, "Re: Looking to buy")
        self.assertIn("Hello Ana,", d.body)
        self.assertFalse(d.needs_review)

    def test_draft_has_compliance_footer(self):
        d, _ = make("buyer@sunshinewholesale.example", HOT)
        self.assertIn(BIZ.postal_address, d.body)
        self.assertIn('reply "STOP"', d.body)

    def test_unverified_draft_asks_for_license_and_needs_review(self):
        d, _ = make("buyer@palmmotors.example", "I want to buy 30 trucks, do you have any available?")
        self.assertTrue(d.needs_review)
        self.assertIn("dealer license", d.body)

    def test_ignored_mail_gets_no_draft(self):
        d, _ = make("x@x.example", "Invoice INV-1 amount due", subject="Invoice")
        self.assertIsNone(d)

    def test_suppressed_sender_gets_no_draft(self):
        supp = SuppressionList()
        supp.add("buyer@sunshinewholesale.example")
        d, _ = make("buyer@sunshinewholesale.example", HOT, supp=supp)
        self.assertIsNone(d)

    def test_approve_flow(self):
        d, supp = make("buyer@sunshinewholesale.example", HOT)
        d = edit(d, body=d.body + "\nP.S. Happy to call.")
        d = approve(d, supp)
        self.assertEqual(d.status, DraftStatus.APPROVED)
        with self.assertRaises(DraftError):
            reject(d)
        with self.assertRaises(DraftError):
            edit(d, subject="x")

    def test_opt_out_after_drafting_blocks_approval(self):
        d, supp = make("buyer@sunshinewholesale.example", HOT)
        supp.add("buyer@sunshinewholesale.example")
        with self.assertRaises(DraftError):
            approve(d, supp)

    def test_cannot_approve_after_removing_opt_out_line(self):
        d, supp = make("buyer@sunshinewholesale.example", HOT)
        d = edit(d, body="Hi there")
        with self.assertRaises(DraftError):
            approve(d, supp)

    def test_reject(self):
        d, _ = make("buyer@sunshinewholesale.example", HOT)
        self.assertEqual(reject(d).status, DraftStatus.REJECTED)


if __name__ == "__main__":
    unittest.main()
