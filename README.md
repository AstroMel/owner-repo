# Wheelie Wholesale

Inbound email sorter for a wholesale car business. See `docs/PROJECT.md` for the plan.

Stage 1 (this code): `wheelie.classify(Email)` labels mail as lead, dealer, supplier, invoice, spam or unknown. It is read-only, extracts claimed dealer license codes, vehicle/volume mentions, and flags opt-out requests (STOP/unsubscribe) for same-day suppression.

Stage 2: `wheelie.verify(email, registry)` checks a claimed dealer license against a state records CSV (`DealerRegistry.from_csv`; columns in `wheelie/licenses.py`). Only an active VW/VI/VA match with a consistent sender domain is `verified`. Domain/name-only matches, free-mail senders and domain mismatches are `review`; inactive, wrong-type and unknown licenses are rejected. `tests/data/dealers_sample.csv` is made-up sample data, not real records.

Stage 3: `SuppressionList(path)` is a SQLite-backed, append-only opt-out list (email and text channels kept separate). `record_opt_out(email, classification, list)` suppresses the sender when the sorter flags an opt-out; repeats are no-ops. `can_contact(address)` must be checked before any draft is created, and it fails closed on addresses it cannot parse. Each entry stores when it was logged and a backstop "honor by" date (10 business days for email, 15 days for text); the goal is same-day. Holidays are ignored, which only makes the deadline early.

Stage 4: `score(email, classification, verification, suppression)` returns a 0-100 score, a tier (hot/warm/cold/drop), an action (draft/review/ignore) and the reasons behind each point. Opt-outs, suppressed senders and non-lead categories drop to zero first. A verified active license is worth the most, then a named vehicle, volume, and a registered address that doesn't look like a PO box or apartment. Bad license evidence caps the score (inactive 20, not found 25, wrong type 30, auction dealer 45). Only a hot score with a verified license gets `draft`, and a draft still waits for your approval. The office-address check is a heuristic on the registry address, not a real inspection.

Run tests: `python3 -m unittest discover -s tests -t .`
