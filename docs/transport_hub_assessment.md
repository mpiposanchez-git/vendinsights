# Transport Hub Assessment

## 1️⃣ Project Overview

| Item | Details |
| --- | --- |
| Goal | Deploy a single dual-zone vending machine (snacks + sandwiches + drinks) in a high-traffic Manchester transport hub (train station or major bus interchange), stream raw MQTT telemetry to your zero-cost dashboard, and evaluate whether the hub model scales. |
| Budget | ≤ £6,000 total CAPEX (machine + installation + contingency + marketing) |
| Timeline | 2–3 months from order to go-live |
| Technical need | Built-in EMV contactless reader and native MQTT telemetry (raw data) |
| Stakeholders | Founder, transport-authority liaison, NICEIC-registered electrician, vending-machine supplier, security team (CCTV) |

## 2️⃣ Options Considered & Final Decision

| Option | Specs | Price | Warranty | Integration Risk | Decision |
| --- | --- | --- | --- | --- | --- |
| New, brand-new unit | Dual-zone, 80 slots, EMV, native MQTT, stainless-steel exterior (suitable for public spaces) | £3,200–£5,000 (Global Vending Group) | 2 years | Very low (no extra gateway needed) | **Chosen** – easiest integration, full warranty, still leaves > £1,000 for other costs |
| Refurbished + MQTT gateway | Same specs, needs external gateway (≈ £150–£250) and possibly separate EMV module | £1,500–£2,500 (Vendtrade) | 12 months (extendable) | Medium (extra hardware & config) | Rejected – cheaper but adds integration steps |
| Refurbished, no reader, add-on both | Same as above, plus both gateway and EMV module | £1,800–£2,200 + add-ons | 12 months | Medium-high (two extra components) | Rejected – lowest cost but more points of failure |

### Rationale

- Integration simplicity is vital because you have no vending-machine experience.
- Warranty reduces risk of early failure, especially in a public, high-traffic environment where downtime can be costly.
- Even at the high end (£5k), total stays under the £6k cap, leaving room for higher licence fees, extra security hardware, and larger contingency.

## 3️⃣ Evaluation Criteria (same weights as gym assessment)

| # | Criterion | Weight | Scoring guide |
| --- | --- | --- | --- |
| 1 | Telemetry (raw MQTT) | 20 | 5 = native, 4 = gateway, 0 = none |
| 2 | Contactless EMV reader | 20 | 5 = built-in, 3 = retrofit, 0 = cash |
| 3 | Product flexibility (snacks, sandwiches, drinks) | 15 | 5 = dual-zone, easy tray swaps |
| 4 | Capacity (≥ 60 slots) | 10 | 5 = ≥ 80, 3 = 60–79, 0 = < 60 |
| 5 | Power & connectivity (Wi-Fi + Ethernet) | 10 | 5 = both, 3 = one, 0 = none |
| 6 | Reliability / warranty | 8 | 5 = ≥ 2 years, 3 = 1 year, 0 = none |
| 7 | CAPEX (≤ £6k) | 7 | 5 = £2–3k, 3 = £3–4k, 0 = > £4k |
| 8 | Operating cost (energy < 1kW) | 5 | 5 = ≤ 1kW |
| 9 | Regulatory compliance (public-space licence, safety) | 3 | 5 = fully compliant, 0 = non-compliant |
| 10 | Scalability (open API) | 2 | 5 = open SDK, 0 = closed |

Scoring process is identical to the gym assessment: assign 0–5 per criterion, multiply by weight, and sum to a max score of 100 (higher is better).

## 4️⃣ Decision Matrix Template (copy-paste into Excel/Sheets)

| Candidate | C1 raw | C1 weighted | C2 reader | C2 weighted | C3 flexibility | C3 weighted | C4 capacity | C4 weighted | C5 power | C5 weighted | C6 reliability | C6 weighted | C7 capex | C7 weighted | C8 opex | C8 weighted | C9 compliance | C9 weighted | C10 scale | C10 weighted | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Example A | 5 | 100 | 5 | 100 | 5 | 75 | 5 | 50 | 5 | 50 | 5 | 40 | 5 | 35 | 5 | 25 | 5 | 15 | 5 | 10 | 560 |
| Example B | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … | … |

## 5️⃣ Budget Snapshot (Transport Hub)

| Cost Item | Estimate | Notes |
| --- | --- | --- |
| New dual-zone machine (80 slots, EMV, native MQTT) | £3,200–£5,000 | Same spec as gym; stainless-steel casing for public use |
| Electrician (public-space certified; possible extra inspection) | £350–£450 | Slight premium for transport-authority-approved tradesperson |
| Licence / council fee (public-space vending licence) | £300–£500 | Required by Manchester City Council / station operator |
| Contingency | £1,000–£1,500 | Covers licence variability, security hardware (tamper alarm/CCTV lock), unforeseen access charges |
| Marketing | £40–£70 | QR-code sticker + bright “Grab-&-Go” banner |
| **Total (max)** | **≈ £5,820** | Still under £6k, with modest buffer |

## 6️⃣ Next Concrete Steps (Transport Hub)

| # | Action | Owner | Target |
| --- | --- | --- | --- |
| 1 | Send quote-request email to at least 3 vendors | Founder | 2026-03-06 |
| 2 | Apply for Manchester City Council public-space vending licence | Founder | 2026-03-08 |
| 3 | Obtain station/operator permission (e.g., Network Rail or TfGM) and any required security clearance | Founder | 2026-03-12 |
| 4 | Collect quotes, fill decision matrix, pick supplier | Founder | 2026-03-15 |
| 5 | Hire council-approved electrician (get 2 quotes) | Founder | 2026-03-16 |
| 6 | Order QR-code stickers and bright “Grab-&-Go” banner | Founder | 2026-03-18 |
| 7 | Schedule delivery and installation (coordinate electrician + security team) | Founder + Supplier | 2026-04-01 |
| 8 | Load initial stock (high-impulse items: bottled water, energy drinks, snack bars) | Founder | 2026-04-02 |
| 9 | Verify MQTT stream appears in dashboard (run test transaction) | Founder | 2026-04-02 |
| 10 | Go live and promote via QR code, station announcements, and commuter-focused social posts | Founder | 2026-04-03 |
| 11 | Log daily sales, telemetry uptime, and security incidents; add weekly summary to `decision_log.json` | Founder | Ongoing |

## 7️⃣ Quote-Request Email Template (Transport Hub)

**Subject:** Quote request – New dual-zone vending machine (≈80 slots) with EMV contactless & MQTT telemetry

Dear [Supplier],

I am launching a vending-machine pilot in Manchester (target location: **major transport hub — train station or bus interchange**) and need a **new** dual-zone (refrigerated + ambient) vending machine with:

- Approximately 80 total slots (≈50 snack, 30 drink)
- Built-in EMV contactless card reader
- Native MQTT telemetry output (raw data)
- Standard 2-year manufacturer warranty
- Delivery and installation timeframe of 2–3 months
- Suitability for public-space deployment (stainless-steel exterior, tamper-resistant design preferred)

Please provide:

1. Unit price (incl. VAT)
2. Lead time for delivery & installation
3. Payment terms
4. Optional accessories (e.g., extra trays, remote diagnostics, security lock)
5. Confirmation of compliance with Manchester public-space vending licence requirements

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
- Suitability for public-space deployment (stainless-steel exterior, tamper-resistant design preferred)

Please provide:

1. Unit price (incl. VAT)
2. Lead time for delivery & installation
3. Payment terms
4. Any optional accessories (e.g., extra trays, remote diagnostics, security lock)
5. Confirmation that the machine complies with Manchester City Council public-space vending licence requirements.

Thank you,

[Your Name]
Vendo-Insights – Manchester
[Phone] | [Email]
"""
        return body


print(build_quote_email("Crane UK", "major transport hub – Manchester train station"))
```

## 9️⃣ Vending-Machine 101 (beginner glossary)

| Term | Meaning |
| --- | --- |
| Dual-zone | Two temperature compartments: refrigerated (drinks/sandwiches) and ambient (snacks). |
| EMV contactless reader | Card standard used by Visa/Mastercard/Apple Pay/Google Pay for tap-to-pay. |
| MQTT | Lightweight publish-subscribe IoT protocol. Machine publishes events (sales, inventory, errors); backend subscribes and stores raw data. |
| CAPEX | Upfront capital spend (machine, installation, etc.). |
| Contingency | Reserve (typically 10–20% of CAPEX) for unexpected costs (wiring, spare parts, licence/security hardware). |
| Public-space licence | Permission from city council or station operator to place a vending machine in a transport hub. |
| Revenue-share | Venue takes a percentage of sales instead of fixed rent. |
| Zero-cost dashboard | Free-tier app receives MQTT data and displays metrics. |
| Zero-cost email handling | Existing free-tier email service can send weekly summaries. |
| Foot-traffic | Number of people passing the location daily. |
| Dwell-time | How long visitors stay in the area; transport hubs usually have short dwell-time, favoring impulse buys. |

## 🔟 Decision-Log Entry (Transport Hub)

```json
{
        "id": "LOC-TH-001",
        "date": "2026-03-02",
        "category": "LocationSelection",
        "description": "Assessed transport hub (Manchester train station / bus interchange) as pilot location – very high foot-traffic, short dwell-time, requires public-space licence and extra security.",
        "rationale": "Largest daily visitor count among the three sites; impulse-purchase environment suits vending. Added complexity of licence and security is offset by high volume potential.",
        "outcome": null,
        "stakeholder": "Founder",
        "estimatedImpact": "Projected £8,000-£22,000 monthly gross once machine is live (based on average £0.90-£1.50 ticket size and 300-500 daily transactions).",
        "risk": "Medium-High – depends on obtaining council licence, station operator approval, and implementing adequate security measures."
}
```
