# University Hall Assessment

## 1️⃣ Project Overview

| Item | Details |
| --- | --- |
| Goal | Deploy a single dual-zone vending machine (snacks + sandwiches + drinks) in a Manchester university residence hall, stream raw MQTT telemetry to your zero-cost dashboard, and evaluate scalability. |
| Budget | ≤ £6,000 total CAPEX |
| Timeline | 2–3 months from order to go-live |
| Technical need | Built-in EMV contactless reader and native MQTT telemetry (raw data) |
| Stakeholders | Founder, university estates team, NICEIC-registered electrician, vending-machine supplier |

## 2️⃣ Options Considered & Final Decision

| Option | Specs | Price | Warranty | Integration Risk | Decision |
| --- | --- | --- | --- | --- | --- |
| New, brand-new unit | Dual-zone, 80 slots, EMV, native MQTT | £3,200–£5,000 (Global Vending Group) | 2 years | Very low (no extra gateway needed) | **Chosen** – simplest integration, full warranty, still leaves > £1,000 for other costs |
| Refurbished + MQTT gateway | Same specs, needs external gateway (≈ £150–£250) and possibly separate EMV module | £1,500–£2,500 (Vendtrade) | 12 months (extendable) | Medium (extra hardware & config) | Rejected – cheaper but adds integration steps |
| Refurbished, no reader, add-on both | Same as above, plus both gateway and EMV module | £1,800–£2,200 + add-ons | 12 months | Medium-high (two extra components) | Rejected – lowest cost but more points of failure |

### Rationale

- Integration simplicity is critical because you have no vending-machine experience.
- Warranty reduces risk of early failure, especially in a university environment where downtime can affect many users.
- Even at the high end (£5k), total spend stays under the £6k cap, leaving room for electrician, contingency, and marketing.

## 3️⃣ Evaluation Criteria (same weights as gym assessment)

| # | Criterion | Weight | Scoring guide |
| --- | --- | --- | --- |
| 1 | Telemetry (raw MQTT) | 20 | 5 = native, 4 = gateway, 0 = none |
| 2 | Contactless EMV reader | 20 | 5 = built-in, 3 = retrofit, 0 = cash |
| 3 | Product flexibility | 15 | 5 = dual-zone, easy tray swaps |
| 4 | Capacity (≥ 60 slots) | 10 | 5 = ≥ 80, 3 = 60–79, 0 = < 60 |
| 5 | Power & connectivity | 10 | 5 = Wi-Fi + Ethernet, 3 = one, 0 = none |
| 6 | Reliability / warranty | 8 | 5 = ≥ 2 years, 3 = 1 year, 0 = none |
| 7 | CAPEX (≤ £6k) | 7 | 5 = £2–3k, 3 = £3–4k, 0 = > £4k |
| 8 | Operating cost (energy < 1kW) | 5 | 5 = ≤ 1kW |
| 9 | Regulatory compliance (food-hygiene, CE) | 3 | 5 = fully compliant |
| 10 | Scalability (open API) | 2 | 5 = open SDK |

Scoring process is identical to the gym assessment: assign 0–5 for each criterion, multiply by weight, and sum to a max score of 100 (higher is better).

## 4️⃣ Decision Matrix Template (copy-paste into Excel/Sheets)

| Candidate | C1 raw | C1 weighted | C2 reader | C2 weighted | C3 flexibility | C3 weighted | C4 capacity | C4 weighted | C5 power | C5 weighted | C6 reliability | C6 weighted | C7 capex | C7 weighted | C8 opex | C8 weighted | C9 compliance | C9 weighted | C10 scale | C10 weighted | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Example A | 5 | 100 | 5 | 100 | 5 | 75 | 5 | 50 | 5 | 50 | 5 | 40 | 5 | 35 | 5 | 25 | 5 | 15 | 5 | 10 | 560 |
| Example B | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … |

## 5️⃣ Budget Snapshot (University Hall)

| Cost Item | Estimate | Notes |
| --- | --- | --- |
| New dual-zone machine (80 slots, EMV, native MQTT) | £3,200–£5,000 | Same spec as gym |
| Electrician (university-approved; possible extra paperwork) | £350–£450 | Slight premium for vetted tradesperson |
| Contingency | £900–£1,200 | Covers extra health-hygiene paperwork and possible licence fees |
| Marketing | £70–£90 | QR-code stickers + student-discount flyer |
| **Total (max)** | **≈ £5,640** | Still under £6k, with modest buffer |

## 6️⃣ Next Concrete Steps (University Hall)

| # | Action | Owner | Target |
| --- | --- | --- | --- |
| 1 | Send quote-request email to at least 3 vendors | Founder | 2026-03-06 |
| 2 | Obtain university estate approval (health-hygiene registration + fire-safety risk assessment) | Founder | 2026-03-12 |
| 3 | Collect quotes, fill decision matrix, pick supplier | Founder | 2026-03-15 |
| 4 | Hire university-approved electrician (get 2 quotes) | Founder | 2026-03-16 |
| 5 | Order QR-code stickers and student-discount flyer | Founder | 2026-03-18 |
| 6 | Schedule delivery and installation (coordinate electrician) | Founder + Supplier | 2026-04-01 |
| 7 | Load initial stock (include healthy options) | Founder | 2026-04-02 |
| 8 | Verify MQTT stream appears in dashboard (run test transaction) | Founder | 2026-04-02 |
| 9 | Go live and promote via QR code, notice board, and student mailing list | Founder | 2026-04-03 |
| 10 | Log daily sales and telemetry; add weekly summary to `decision_log.json` | Founder | Ongoing |

## 7️⃣ Quote-Request Email Template (University Hall)

**Subject:** Quote request – New dual-zone vending machine (≈80 slots) with EMV contactless & MQTT telemetry

Dear [Supplier],

I am launching a vending-machine pilot in Manchester (target location: **university residence hall**) and need a **new** dual-zone (refrigerated + ambient) vending machine with:

- Approximately 80 total slots (≈50 snack, 30 drink)
- Built-in EMV contactless card reader
- Native MQTT telemetry output (raw data)
- Standard 2-year manufacturer warranty
- Delivery and installation timeframe of 2–3 months

Please provide:

1. Unit price (incl. VAT)
2. Lead time for delivery & installation
3. Payment terms
4. Optional accessories (e.g., extra trays, remote diagnostics)

Thank you,

[Your Name]  
Vendo-Insights – Manchester  
[Phone] | [Email]

## 8️⃣ Tiny Python Helper (same email body)

```python
def build_quote_email(supplier_name: str, location: str) -> str:
        """Returns a ready-to-send email body for vending-machine quote requests."""
        subject = "Quote request – New dual-zone vending machine (≈80 slots) with EMV contactless & MQTT telemetry"
        body = f"""Subject: {subject}

Dear {supplier_name},

I am launching a vending-machine pilot in Manchester (target location: {location}) and need a **new** dual-zone (refrigerated + ambient) vending machine with:

- Approximately 80 total slots (≈50 snack, 30 drink)
- Built-in EMV contactless card reader
- Native MQTT telemetry output (raw data)
- Standard 2-year manufacturer warranty
- Delivery and installation timeframe of 2–3 months

Please provide:

1. Unit price (incl. VAT)
2. Lead time for delivery & installation
3. Payment terms
4. Any optional accessories (e.g., extra trays, remote diagnostics)

Thank you,

[Your Name]
Vendo-Insights – Manchester
[Phone] | [Email]
"""
        return body


print(build_quote_email("Crane UK", "university residence hall"))
```

## 9️⃣ Vending-Machine 101 (beginner glossary)

| Term | Meaning |
| --- | --- |
| Dual-zone | Two temperature compartments: refrigerated (drinks/sandwiches) and ambient (snacks). |
| EMV contactless reader | Card standard used by Visa/Mastercard/Apple Pay/Google Pay for tap-to-pay. |
| MQTT | Lightweight publish-subscribe IoT protocol. Machine publishes events (sales, inventory, errors); backend subscribes and stores raw data. |
| CAPEX | Upfront capital spend (machine, installation, etc.). |
| Contingency | Reserve (typically 10–20% of CAPEX) for unexpected costs. |
| Revenue-share | Venue takes a percentage of machine sales instead of fixed rent. |
| Zero-cost dashboard | Free-tier app receives MQTT data and displays metrics. |
| Zero-cost email handling | Existing free-tier email service can send weekly summaries. |
| Foot-traffic | Number of people passing the location per day. |
| Dwell-time | How long visitors stay in the area; longer dwell-time can increase spend. |

## 🔟 Decision-Log Entry (University Hall)

```json
{
        "id": "LOC-UH-001",
        "date": "2026-03-02",
        "category": "LocationSelection",
        "description": "Assessed university hall as pilot location – high foot-traffic, diverse product demand, but requires university health-hygiene registration and estate approval.",
        "rationale": "Largest daily visitor count among the three sites; strong lunchtime demand; willingness to accept contactless payment. Added complexity of university approvals is offset by higher revenue potential.",
        "outcome": null,
        "stakeholder": "Founder",
        "estimatedImpact": "Projected £7,000-£10,000 monthly gross once machine is live.",
        "risk": "Medium-High – depends on obtaining university estate approval, health-hygiene registration, and electrician availability."
}
```
