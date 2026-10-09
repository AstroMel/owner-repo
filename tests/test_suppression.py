import os
import tempfile
import unittest
from datetime import date, datetime, timezone

from wheelie import Email, classify
from wheelie.suppression import (
    SuppressionList,
    add_business_days,
    honor_by,
    normalize_address,
    record_opt_out,
)


class NormalizeTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_address("Jo Smith <Jo@Example.COM>"), "jo@example.com")
        self.assertEqual(normalize_address("  a@b.co "), "a@b.co")
        self.assertEqual(normalize_address("not an address"), "")
        self.assertEqual(normalize_address(""), "")


class DeadlineTests(unittest.TestCase):
    def test_business_days_skip_weekends(self):
        # Fri 2026-10-09 + 1 business day = Mon 2026-10-12
        self.assertEqual(add_business_days(date(2026, 10, 9), 1), date(2026, 10, 12))
        self.assertEqual(add_business_days(date(2026, 10, 9), 10), date(2026, 10, 23))

    def test_channel_deadlines(self):
        d = date(2026, 10, 9)
        self.assertEqual(honor_by("email", d), date(2026, 10, 23))
        self.assertEqual(honor_by("text", d), date(2026, 10, 24))


class ListTests(unittest.TestCase):
    def setUp(self):
        self.s = SuppressionList()

    def test_add_and_check(self):
        self.assertTrue(self.s.can_contact("a@x.com"))
        self.assertTrue(self.s.add("A@X.com"))
        self.assertTrue(self.s.is_suppressed("a@x.com"))
        self.assertTrue(self.s.is_suppressed("Someone <a@x.com>"))
        self.assertTrue(self.s.can_contact("b@x.com"))

    def test_add_is_idempotent(self):
        self.assertTrue(self.s.add("a@x.com"))
        self.assertFalse(self.s.add("a@x.com"))
        self.assertEqual(len(self.s), 1)

    def test_channels_are_separate(self):
        self.s.add("a@x.com", channel="text")
        self.assertTrue(self.s.is_suppressed("a@x.com", "text"))
        self.assertFalse(self.s.is_suppressed("a@x.com", "email"))

    def test_unparseable_address_fails_closed(self):
        self.assertTrue(self.s.is_suppressed("garbage"))
        with self.assertRaises(ValueError):
            self.s.add("garbage")

    def test_unknown_channel_rejected(self):
        with self.assertRaises(ValueError):
            self.s.add("a@x.com", channel="fax")

    def test_entry_records_deadline(self):
        now = datetime(2026, 10, 9, 15, 0, tzinfo=timezone.utc)
        self.s.add("a@x.com", now=now, reason="STOP reply")
        (e,) = self.s.entries()
        self.assertEqual(e.honor_by, date(2026, 10, 23))
        self.assertEqual(e.reason, "STOP reply")

    def test_persists_across_connections(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.db")
            first = SuppressionList(path)
            first.add("a@x.com")
            first.close()
            second = SuppressionList(path)
            self.assertTrue(second.is_suppressed("a@x.com"))
            second.close()


class PipelineTests(unittest.TestCase):
    def test_stop_reply_suppresses_sender(self):
        s = SuppressionList()
        mail = Email("Buyer <buyer@dealer.example>", "Re: Looking to buy cars", "STOP")
        self.assertTrue(record_opt_out(mail, classify(mail), s))
        self.assertTrue(s.is_suppressed("buyer@dealer.example"))
        # reprocessing the same message changes nothing
        self.assertFalse(record_opt_out(mail, classify(mail), s))
        self.assertEqual(len(s), 1)

    def test_normal_mail_not_suppressed(self):
        s = SuppressionList()
        mail = Email("buyer@dealer.example", "Trucks", "I want to buy 10 trucks, do you have any available?")
        self.assertFalse(record_opt_out(mail, classify(mail), s))
        self.assertEqual(len(s), 0)


if __name__ == "__main__":
    unittest.main()
