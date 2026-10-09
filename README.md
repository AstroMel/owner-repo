# Wheelie Wholesale

Inbound email sorter for a wholesale car business. See `docs/PROJECT.md` for the plan.

Stage 1 (this code): `wheelie.classify(Email)` labels mail as lead, dealer, supplier, invoice, spam or unknown. It is read-only, extracts claimed dealer license codes, vehicle/volume mentions, and flags opt-out requests (STOP/unsubscribe) for same-day suppression.

Stage 2: `wheelie.verify(email, registry)` checks a claimed dealer license against a state records CSV (`DealerRegistry.from_csv`; columns in `wheelie/licenses.py`). Only an active VW/VI/VA match with a consistent sender domain is `verified`. Domain/name-only matches, free-mail senders and domain mismatches are `review`; inactive, wrong-type and unknown licenses are rejected. `tests/data/dealers_sample.csv` is made-up sample data, not real records.

Stage 3: `SuppressionList(path)` is a SQLite-backed, append-only opt-out list (email and text channels kept separate). `record_opt_out(email, classification, list)` suppresses the sender when the sorter flags an opt-out; repeats are no-ops. `can_contact(address)` must be checked before any draft is created, and it fails closed on addresses it cannot parse. Each entry stores when it was logged and a backstop "honor by" date (10 business days for email, 15 days for text); the goal is same-day. Holidays are ignored, which only makes the deadline early.

Run tests: `python3 -m unittest discover -s tests -t .`
