import unittest
from pathlib import Path

from wheelie import DealerRegistry, Email, SuppressionList, classify, verify
from wheelie.licenses import DealerRecord, Status, Verification
from wheelie.scoring import Action, Tier, looks_like_non_office, score

REGISTRY = DealerRegistry.from_csv(Path(__file__).parent / "data" / "dealers_sample.csv")


def run(sender, body, subject="Looking to buy", suppression=None):
    mail = Email(sender, subject, body)
    return score(mail, classify(mail), verify(mail, REGISTRY), suppression)


class ScoringTests(unittest.TestCase):
    def test_verified_with_vehicle_and_volume_is_hot_and_drafts(self):
        s = run("buyer@sunshinewholesale.example",
                "We are looking to buy 20 SUVs. Dealer license VW12345. Do you have any available?")
        self.assertEqual(s.tier, Tier.HOT)
        self.assertEqual(s.action, Action.DRAFT)
        self.assertGreaterEqual(s.value, 70)

    def test_verified_without_specifics_is_warm_review(self):
        s = run("buyer@sunshinewholesale.example", "Interested in buying from you. License VW12345.")
        self.assertEqual(s.tier, Tier.WARM)
        self.assertEqual(s.action, Action.REVIEW)

    def test_partial_match_never_drafts(self):
        s = run("buyer@palmmotors.example", "I want to buy 30 trucks, do you have any available?")
        self.assertNotEqual(s.action, Action.DRAFT)

    def test_unverified_claim_is_capped_cold(self):
        s = run("x@x.example", "I want to buy 50 cars. Dealer license VW99999. Do you have any available?")
        self.assertLessEqual(s.value, 25)
        self.assertEqual(s.action, Action.IGNORE)

    def test_inactive_license_is_capped(self):
        s = run("a@oldlot.example", "I want to buy 50 cars. License VW44444. Do you have any available?")
        self.assertLessEqual(s.value, 20)
        self.assertEqual(s.action, Action.IGNORE)

    def test_wrong_license_type_is_capped(self):
        s = run("a@citrusford.example", "I want to buy 50 cars. License VF33333. Do you have any available?")
        self.assertLessEqual(s.value, 30)

    def test_non_lead_category_dropped(self):
        s = run("a@x.example", "Invoice INV-1 amount due, remit within 30 days", subject="Invoice")
        self.assertEqual(s.tier, Tier.DROP)

    def test_opt_out_dropped(self):
        s = run("buyer@sunshinewholesale.example", "STOP", subject="Re: Looking to buy cars")
        self.assertEqual(s.tier, Tier.DROP)

    def test_suppressed_sender_dropped_even_if_hot(self):
        supp = SuppressionList()
        supp.add("buyer@sunshinewholesale.example")
        s = run("buyer@sunshinewholesale.example",
                "We are looking to buy 20 SUVs. License VW12345. Do you have any available?", suppression=supp)
        self.assertEqual(s.tier, Tier.DROP)
        self.assertEqual(s.action, Action.IGNORE)

    def test_auction_dealer_capped(self):
        reg = DealerRegistry([DealerRecord("VA77777", "Auction House", "VA", "Active", address="1 Main St")])
        mail = Email("a@gmail.com", "Looking to buy", "I want to buy 40 cars. License VA77777. Do you have any?")
        v = verify(mail, reg)
        self.assertEqual(v.status, Status.VERIFIED)
        s = score(mail, classify(mail), v)
        self.assertLessEqual(s.value, 45)
        self.assertNotEqual(s.action, Action.DRAFT)

    def test_po_box_address_penalized(self):
        reg = DealerRegistry([DealerRecord("VW88888", "Box Autos", "VW", "Active", address="PO Box 12 Orlando FL")])
        mail = Email("a@gmail.com", "Looking to buy", "I want to buy 20 cars. License VW88888.")
        s = score(mail, classify(mail), verify(mail, reg))
        self.assertTrue(any("PO box" in r for r in s.reasons))

    def test_office_heuristic(self):
        self.assertTrue(looks_like_non_office("PO Box 5"))
        self.assertTrue(looks_like_non_office("12 Oak St Apt 4"))
        self.assertFalse(looks_like_non_office("100 Example Way Orlando FL"))

    def test_reasons_explain_score(self):
        s = run("buyer@sunshinewholesale.example",
                "We are looking to buy 20 SUVs. License VW12345. Do you have any available?")
        self.assertTrue(any("verified VW" in r for r in s.reasons))


if __name__ == "__main__":
    unittest.main()
