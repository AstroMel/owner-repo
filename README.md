# Wheelie Wholesale

Inbound email sorter for a wholesale car business. See `docs/PROJECT.md` for the plan.

Stage 1 (this code): `wheelie.classify(Email)` labels mail as lead, dealer, supplier, invoice, spam or unknown. It is read-only, extracts claimed dealer license codes, vehicle/volume mentions, and flags opt-out requests (STOP/unsubscribe) for same-day suppression.

Stage 2: `wheelie.verify(email, registry)` checks a claimed dealer license against a state records CSV (`DealerRegistry.from_csv`; columns in `wheelie/licenses.py`). Only an active VW/VI/VA match with a consistent sender domain is `verified`. Domain/name-only matches, free-mail senders and domain mismatches are `review`; inactive, wrong-type and unknown licenses are rejected. `tests/data/dealers_sample.csv` is made-up sample data, not real records.

Run tests: `python3 -m unittest discover -s tests -t .`
