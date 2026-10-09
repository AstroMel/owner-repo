import unittest

from wheelie import Category, Email, classify


def mail(subject, body, **headers):
    return Email("a@example.com", subject, body, headers)


class SorterTests(unittest.TestCase):
    def test_lead(self):
        r = classify(mail("Looking for trucks", "I want to buy 12 trucks, mostly Ford. Do you have any available?"))
        self.assertEqual(r.category, Category.LEAD)
        self.assertTrue(r.mentions_vehicle)
        self.assertTrue(r.mentions_volume)

    def test_dealer_with_license_claim(self):
        r = classify(mail("Wholesale partner", "We are a licensed wholesale dealer, license VW, buying sedans."))
        self.assertEqual(r.category, Category.DEALER)
        self.assertEqual(r.claimed_license_codes, ("VW",))

    def test_codes_ignored_without_license_context(self):
        r = classify(mail("Hi", "Meet at VI street at noon."))
        self.assertEqual(r.claimed_license_codes, ())

    def test_invoice(self):
        r = classify(mail("Invoice INV-2041", "Amount due: see attached. Remit within 30 days."))
        self.assertEqual(r.category, Category.INVOICE)

    def test_supplier(self):
        r = classify(mail("Our services", "We offer detailing and towing. Quote for your lot, our rates attached."))
        self.assertEqual(r.category, Category.SUPPLIER)

    def test_spam(self):
        r = classify(mail("WINNER!!!", "Act now, guaranteed traffic. Click here", **{"List-Unsubscribe": "<x>"}))
        self.assertEqual(r.category, Category.SPAM)

    def test_opt_out_is_flagged_and_not_a_lead(self):
        r = classify(mail("Re: Looking to buy cars", "STOP"))
        self.assertTrue(r.opt_out_request)
        self.assertNotEqual(r.category, Category.LEAD)

    def test_unknown(self):
        r = classify(mail("Hello", "Just saying hi."))
        self.assertEqual(r.category, Category.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
