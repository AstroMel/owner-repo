# Wheelie Wholesale

Inbound email sorter for a wholesale car business. See `docs/PROJECT.md` for the plan.

Stage 1 (this code): `wheelie.classify(Email)` labels mail as lead, dealer, supplier, invoice, spam or unknown. It is read-only, extracts claimed dealer license codes, vehicle/volume mentions, and flags opt-out requests (STOP/unsubscribe) for same-day suppression.

Run tests: `python3 -m unittest discover -s tests -t .`
