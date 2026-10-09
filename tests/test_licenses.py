import unittest
from pathlib import Path

from wheelie import Email
from wheelie.licenses import DealerRegistry, Status, extract_license_numbers, verify

REGISTRY = DealerRegistry.from_csv(Path(__file__).parent / "data" / "dealers_sample.csv")


def check(sender, body, subject="Hello"):
    return verify(Email(sender, subject, body), REGISTRY)


class VerifyTests(unittest.TestCase):
    def test_loads_records(self):
        self.assertEqual(len(REGISTRY), 5)

    def test_extracts_numbers_with_varied_formatting(self):
        self.assertEqual(extract_license_numbers("Dealer license # VW 12345"), ["VW 12345"])
        self.assertEqual(extract_license_numbers("lic: vi-22222."), ["vi-22222"])
        self.assertEqual(extract_license_numbers("Our dealer license is VW12345."), ["VW12345"])
        self.assertEqual(extract_license_numbers("call 407 555 1234"), [])

    def test_verified(self):
        v = check("buyer@sunshinewholesale.example", "Our dealer license VW-12345, buying SUVs.")
        self.assertEqual(v.status, Status.VERIFIED)
        self.assertTrue(v.passes_filter)

    def test_verified_when_registry_has_no_domain(self):
        v = check("x@example.org", "License number VI55555")
        self.assertEqual(v.status, Status.VERIFIED)

    def test_domain_mismatch_goes_to_review(self):
        v = check("someone@other.example", "License VW12345")
        self.assertEqual(v.status, Status.REVIEW)
        self.assertFalse(v.passes_filter)

    def test_free_mail_goes_to_review(self):
        v = check("someone@gmail.com", "License VW12345")
        self.assertEqual(v.status, Status.REVIEW)

    def test_inactive(self):
        v = check("a@oldlot.example", "License VW44444")
        self.assertEqual(v.status, Status.INACTIVE)

    def test_ineligible_type(self):
        v = check("a@citrusford.example", "License VF33333")
        self.assertEqual(v.status, Status.INELIGIBLE_TYPE)

    def test_unknown_number(self):
        v = check("a@x.example", "License VW99999")
        self.assertEqual(v.status, Status.NOT_FOUND)

    def test_domain_alone_never_passes(self):
        v = check("a@palmmotors.example", "Interested in your inventory")
        self.assertEqual(v.status, Status.REVIEW)

    def test_name_alone_never_passes(self):
        v = check("a@gmail.com", "This is Palm Motors, interested in inventory")
        self.assertEqual(v.status, Status.REVIEW)

    def test_no_claim(self):
        v = check("a@gmail.com", "Want to buy a car")
        self.assertEqual(v.status, Status.NO_CLAIM)


if __name__ == "__main__":
    unittest.main()
