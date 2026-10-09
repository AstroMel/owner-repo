# Wheelie Wholesale

Orlando, Florida · wholesale car leads

A bot that sorts email, spots leads, and moves them into a CRM for a wholesale car business. It sorts the mail, checks who is a real licensed dealer, and prepares replies for you to approve.

## Options & agent plan

Ten options were ranked from worst to best on how fast each runs and how safe it is (scored 0 to 100). The ranked chart was an embedded item and is not included in the source note, so the full list is not captured here.

- **Worst:** a person doing it by hand with no tools.
- **Best:** a scheduled Claude agent that reads mail, scores leads, and drafts replies. A human still approves anything that sends or touches money.

Source note: "Wholesale Auto Lead Bot — Options & Agent Plan", Oct 9, 2026.

## How a lead moves

Six steps, one human gate:

1. **Email arrives** — one mailbox, read and draft only.
2. **Sorted** — lead, dealer, supplier, invoice, spam.
3. **Verified** — dealer license type and active status.
4. **Scored** — vehicle, volume, real office address.
5. **Drafted** — reply written, not sent.
6. **You approve** — nothing sends without you.

## Research: who your leads should be

Florida law keeps wholesale trade between licensed businesses. A wholesale dealer may buy and sell only with other licensed dealers or through auctions. So a real wholesale lead should hold a state dealer license, and checking that license is the strongest filter the bot has.

| Code | License | What it allows | Lead fit |
| --- | --- | --- | --- |
| VW | Wholesale dealer | Buys and sells only at wholesale, with licensed dealers or at auctions. No retail. | Direct fit |
| VI | Independent dealer | Buys, sells and deals in used vehicles. Needed for any retail used sales. | Strong fit |
| VA | Auction dealer | Sells by bid. Buyers must be licensed dealers. | Channel, not a buyer |
| VF | Franchised dealer | Sells new vehicles for a manufacturer. Limited to approved line-makes. | Check case by case |
| SD | Salvage dealer | Acquires salvaged or wrecked vehicles to resell or part out. | Separate niche |

### Signals of a real wholesale lead

- **Active license** of type VW, VI or VA.
- **A non-residential office.** The statute requires wholesale dealers to keep an office where records are kept.
- **A named vehicle or volume** in the first message.
- **A registered business** that matches the sender's domain and name.

### Rules for contacting people

- **Email (federal).** Accurate headers, honest subject lines, a clear ad label, a postal address, and a working opt-out honored within 10 business days. Penalties reach $53,088 per email.
- **Calls and texts (Florida).** Consent can be a checked box or a text reply. Only unsolicited sales calls need prior written consent, with exceptions for an existing relationship. After a STOP reply, texts must end within 15 days.
- This is general information, not legal advice.

## The best path for this project

1. **Start with inbound mail only.** People who write to you are the lowest risk and the warmest. Add outbound prospecting after the sorting works.
2. **Make license checking the first filter.** It removes most noise before any scoring happens.
3. **Keep a human gate on every send.** The bot drafts. You approve. This also keeps you inside the email and text rules.
4. **Log every opt-out and STOP the same day.** Both rules have short deadlines, so build suppression in from the start.
5. **Grow into agents one job at a time.** Inbox, then verification, then scoring, then drafting. Each can be tested alone before the app wraps them.

## Still open

**Orlando dealer count and a public dealer list.** A public dealer search or download on the state site could not be confirmed, so the number of Orlando dealers is still unknown. The next step is to ask the state for its dealer license records and filter them to Orange County.

- **Inbox access** — one mailbox, read and draft only.
- **CRM access** — read-only, dedicated account.
- **Code repository** — repository name to be confirmed.
- **Dealer records** — state list, Orange County.

## Sources

- [Florida DHSMV: dealer and broker license types](https://www.flhsmv.gov/motor-vehicles-tags-titles/dealers-installers-manufacturers-distributors-importers/mv-rv-mh-dealer-broker-licenses/types-of-licenses-available)
- [Florida DHSMV: dealer license FAQs](https://www.flhsmv.gov/motor-vehicles-tags-titles/dealers-installers-manufacturers-distributors-importers/mv-rv-mh-dealer-broker-licenses/mv-rv-mh-dealers-faqs)
- [Florida Statutes 320.27: motor vehicle dealers](http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0300-0399/0320/Sections/0320.27.html)
- [FTC: CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Summary of the 2023 Florida Telephone Solicitation Act amendments](https://www.mcguirewoods.com/client-resources/alerts/2023/5/pro-business-amendments-to-floridas-mini-tcpa-now-in-effect)

Researched October 9, 2026. Rules change, so confirm with the state and a lawyer before you launch.
