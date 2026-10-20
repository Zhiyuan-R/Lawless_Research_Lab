# Harvey LAB judge bundle — firm-knowledge/tasks/061/claude-code-session/20261016-032331

You are the judge. For EACH criterion below, apply the official LAB per-criterion
prompt independently, as if it were the only criterion: the agent output is the
block it points to, the criterion is its title + text. Do not let one criterion's
verdict influence another, and do not reward effort — judge only what the output says.

Write `/tmp/lab-judging/d039503c62ca/responses.json` as a JSON object mapping every criterion id
to {"reasoning": "...", "verdict": "pass" | "fail"}. All 1 ids must be present.

## Official per-criterion prompt (for reference)

````
You are evaluating a legal AI agent's work product against a specific quality criterion.

## Task
{task_description}

## Agent's Output
{agent_output}

## Criterion
**{criterion_title}**

{match_criteria}

## Instructions
Evaluate the agent's output against the criterion above.
- **PASS**: The agent's output satisfies the criterion as described
- **FAIL**: The agent's output does not satisfy the criterion as described

Respond with JSON only:

```json
{{
  "reasoning": "Brief explanation",
  "verdict": "pass" | "fail"
}}
```

````

## Task
Funds with an American Deal-by-Deal Waterfall

## Agent outputs

<<<OUT-0d96a0d4>>>
## Agent Output: response.md
# Firm History With American (Deal-by-Deal) Waterfalls

**Question:** Have we ever set up a fund using an American, deal-by-deal waterfall?

## Short answer

**No. The firm files show no fund we set up with an operative American (deal-by-deal) waterfall.** Every fund-level distribution waterfall in the files, whether we drafted it, marked it up or reviewed it, is a European (whole-fund) waterfall. In at least two matters we removed or resisted deal-by-deal terms.

There is **one exception you should know about before you tell the client “never”:**

- **ICM Cascadia Co-Invest, LP (Matter 1023-00001, Ironside Capital Management).** The executed side letter dated July 29, 2022 says carried interest “shall be calculated on a deal-by-deal basis with respect to the Cascadia investment.” That is the only executed document in our files that uses deal-by-deal carry language.
- **It is not a real precedent for a deal-by-deal fund.**
  - It is a single-asset co-investment vehicle.
  - We acted for the LP (Ironside), not the sponsor.
  - The executed LPA says expressly that its waterfall is “whole fund.”
  - Our own formation memos call it a European/whole-fund waterfall.
  - The vehicle never made its investment. It has been dormant since January 2023.
- The side letter’s carry section also has drafting defects (details in Section 2).

So if the question is whether we have firm precedent (forms, negotiating experience or a closed fund) for structuring a multi-asset fund on an American waterfall, the answer is no. We would be starting from scratch.

---

## 1. How I searched

- I converted all ~9,300 documents in the firm document set to text: 266 matters, covering .docx, .eml, .xlsx and .pptx.
- I ran full-text searches for: “deal-by-deal” / “deal by deal”, “American waterfall” / “American-style”, “investment-by-investment”, “per-deal” / “per-investment carry”, “realized investment” formulations, and “European” / “whole-fund” waterfall.
- I also searched every document that mentions both “waterfall” and “carried interest”. That turned up 28 matters, most of which use “waterfall” for debt or payment waterfalls and are not relevant.
- I listed every LPA, LLC agreement and operating agreement in the files and checked the waterfall language in each fund-type agreement.
- I read in full, or in all relevant sections, the documents I rely on below.

Most “deal-by-deal” hits have nothing to do with carry. They refer to co-investment offered “on a deal-by-deal basis,” AIVs formed deal by deal, state-tax nexus monitoring, and similar points. I excluded those.

---

## 2. The one instance of deal-by-deal carry language: ICM Cascadia Co-Invest, LP (Matter 1023-00001)

**Client / role:** Ironside Capital Management LP, the limited partner (99.99%, $299.97M commitment). The engagement letter dated July 14, 2022 (Pamela Cross, responsible partner) covers formation of the vehicle and negotiation and drafting of the LPA, side letter and Co-Investment Allocation Agreement.

**Other side:** The GP was Meridian Infrastructure GP IV LLC, represented by Breckenridge Sloane & Pratt LLP. The vehicle was formed to co-invest alongside Meridian Infrastructure Partners Fund IV in a single acquisition (Cascadia Renewables Holdings, Inc.).

**What the documents say:**

| Document | Provision | Waterfall characterization |
|---|---|---|
| Side Letter (executed, July 29, 2022), `Formation/side-letter-ironside-meridian-gp-execution.docx` | §3.4 | “Carried interest shall be calculated on a **deal-by-deal basis with respect to the Cascadia investment**, subject to the clawback mechanism set forth in Section 8.04 of the LP Agreement…” §3.5 says there is no catch-up. |
| LPA (executed, July 29, 2022), `Formation/lp-agreement-icm-co-invest-execution.docx` | §6.02 (Waterfall); §5.02(b)–(c) | Return of capital, then 8% pref (compounded quarterly), then 100% GP catch-up, then 90/10. “For the avoidance of doubt, the distribution waterfall … shall apply on a cumulative basis over the life of the Partnership (i.e., a **‘whole fund’ waterfall**).” |
| LPA | §11.03 | The side letter is incorporated by reference and controls over the LPA “as between the General Partner and the Limited Partner.” Side letter §11.2 says the same. |
| Formation & Governance Summary Memo (C&H, July 25, 2022; T. Kim / P. Cross) | §XI | “structured as a standard **‘whole fund’ or ‘European-style’ waterfall**.” |
| ERISA Benefit Plan Investor Memo (C&H, July 27, 2022) | §C | “This carried interest waterfall is calculated on a **whole-fund basis (as there is only a single investment)**, with a full catch-up.” |
| Co-Investment Allocation Agreement (executed) | §7.01–7.02 | Distributions from AcquisitionCo are split pro rata 71.43% / 28.57%. Carry is determined separately for each party under its own partnership agreement. |
| Tax Structuring Memo (S. Hartwell, July 20, 2022) | §IV.B | Describes a four-step waterfall with a GP catch-up and does not call it deal-by-deal. |

**Why this is not an American-waterfall fund precedent:**

1. **Single-asset vehicle.** The LPA limits the Partnership’s purpose to the Cascadia co-investment. With only one deal, “deal-by-deal” and “whole-fund” produce the same economics. The firm’s own ERISA memo makes this point. The defining risk of an American waterfall is carry paid on early winners before later losers are netted, and that risk cannot arise here.
2. **Wrong side of the table.** We represented the LP. We did not set up a sponsor’s fund on an American waterfall.
3. **The operative LPA is expressly whole-fund.** The side letter’s deal-by-deal wording does override the LPA between these parties under LPA §11.03, so it is technically operative. But it has no economic effect beyond the one-asset point above.
4. **The vehicle never operated.** Meridian issued a capital-call suspension notice under LPA §7.04 on January 9, 2023, and the vehicle has been dormant since. Our filings show no investment, gains or carry. The K-1 reviews for TY2022 and TY2023 and the quarterly reviews confirm that no carried interest was ever accrued. In July 2024 we advised Ironside on its wind-down election right (P. Cross email, July 25, 2024, recommending deferral).

**Drafting defects worth flagging internally.** If anyone pulls this side letter as a “deal-by-deal” form, they should know that it does not match the executed LPA:

- **Article VIII reference.** Side letter §3.1–3.2 says the carry methodology is in “Article VIII of the LP Agreement.” LPA Article VIII is “Liability of Partners.” Carry and the waterfall are in Articles V and VI.
- **Clawback reference.** Side letter §3.4 cites a GP clawback in “Section 8.04 of the LP Agreement.” The LPA has no §8.04 and no GP clawback. LPA §8.01 actually says no distribution to the LP is subject to clawback.
- **Catch-up conflict.** Side letter §3.5 says there is no catch-up “unless otherwise expressly specified in the LP Agreement.” LPA §5.02(c) and §6.02(c) do provide a 100% GP catch-up. Because of the carve-out, the catch-up probably survives. That is the opposite of what the side letter’s “no catch-up” heading suggests.
- **Wrong section numbers.** Side letter recitals cite LPA §12.09 as the side-letter authority, but LPA §12.09 is “No Third-Party Beneficiaries.” The side-letter provision is §11.03. Side letter §13.2 cites LPA §13.02 for dispute resolution, but the LPA’s Article XIII is “Investment Company Act and ERISA.”
- **Inconsistent descriptions in our own later documents.** Later Ironside documents place the waterfall in three different places: LPA §5.01 (reservation-of-rights letter; wind-down election memo), §8.02 (dormancy governance memo) and §6.02 (the LPA itself and the suspension notice).

None of this matters economically while the vehicle is dormant. It does mean this document should not be reused as a template.

---

## 3. Matters where we rejected or replaced deal-by-deal terms

### Pinnacle Continuation Vehicle LP (Matter 1002-00005, Pinnacle Capital Management LLC, sponsor-side tax counsel)

- In C&H’s markup of the CV LPA tax provisions (August 8, 2025; addressed to Hawthorne Reid LLP, which drafted the LPA), §Z.1 comment reads: “The Hawthorne Reid draft contained a **simplified deal-by-deal waterfall** with a flat 20% carry and no preferred return. Per instructions from Marcus Aldren and consistent with the Garrison term sheet dated June 15, 2025, this should be a **European-style (whole-fund) waterfall** with a 7% preferred return and a 15% carry. We have revised accordingly.”
- The issues table in the markup records: “Replaced deal-by-deal waterfall with European-style (whole-fund) waterfall per Garrison term sheet.”
- The engagement letter (July 15, 2025) and the tax structure memorandum also describe the CV carry as European/whole-fund.
- **Takeaway:** This is the only sponsor-side matter where a deal-by-deal waterfall appeared in a draft. It came from other counsel, and the client and the lead secondary investor’s term sheet had it removed.

### Ridgeline-Clarion Co-Invest, L.P. (Matter 1027-00002, Pellegrino Capital Group LLC, LP-side)

- Negotiation tracker, Item 1: Pellegrino, our client, asked for carry “calculated on deal-by-deal basis.” The tracker notes: “Sponsor pushed back on deal-by-deal carry calc. Agreed to whole-fund carry but with reduced rate.” The final term is 10% carry over an 8% pref compounded quarterly, with a “whole-fund (aggregate) carry calculation.” The tracker marks this agreed on January 10, 2026.
- The executed co-invest LPA, §6.2, applies the waterfall “on a cumulative, aggregate basis across all Distributions.” The clawback “Excess Amount” is measured as if all distributions were one liquidating distribution.

---

## 4. Funds we set up or worked on: all European / whole-fund

| Matter | Fund / vehicle | Our role | Waterfall | Key source |
|---|---|---|---|---|
| 1003-00002 | Harrowgate Private Equity Fund V LP (plus parallel fund and offshore feeder) | Sponsor’s fund formation counsel | European / whole-fund, 20% over 8% | Fund Structuring Memo (Apr. 14, 2025): European waterfall “provides greater downside protection … compared to a deal-by-deal (American-style) waterfall and has been a consistent feature of HCP’s fund terms since HPE Fund III.” Also: §1061 memo (May 5, 2025); offshore feeder LPA (“not calculated or distributed on a deal-by-deal basis”); PPM drafts; form distribution notice; sub-facility memo. |
| 1004-00002 | Cobalt Life Sciences Opportunities Fund I, LP | Sponsor’s fund formation counsel | European / whole-fund, 20% over 8%, 100% catch-up, GP clawback with 30% carry escrow | LPA first draft §6.2, “Distribution Waterfall (European / Whole-Fund Waterfall)”; PPM outline; tax memo. |
| 1001-00002 | Ardent Capital Partners III LP (GP/ManCo restructuring) | Sponsor counsel | Whole-fund, European-style | LPAC notification letter (Feb. 5, 2024): “mechanics of carried interest calculation (whole-Fund, European-style waterfall) remain unchanged.” Carried Interest Allocation Agreement: catch-up “calculated on a whole-Fund, aggregate basis (not on an investment-by-investment basis).” |
| 1002-00003 | Pinnacle Venture Fund II LP (side letters / MFN) | Sponsor counsel | Whole-fund; “standard European-style clawback” | Closing checklist / side-letter package. |
| 1002-00005 | Pinnacle Continuation Vehicle LP | Sponsor tax counsel | European / whole-fund (deal-by-deal draft rejected) | See Section 3. |
| 1041-00005 | Solara Consolidated Master Fund LP (reorganization) | Sponsor counsel | Cumulative return of capital / pref / catch-up structure. Economic terms are still bracketed in the draft, and existing Fund IV/V waterfalls are “unchanged.” | Master Fund LPA draft §6.2; draft Fund V LPA amendment. |
| 1023-00001 | ICM Cascadia Co-Invest, LP | LP counsel | LPA: whole-fund. Side letter: “deal-by-deal” for the single asset. | See Section 2. |
| 1027-00002 | Ridgeline-Clarion Co-Invest, L.P. | LP counsel | Whole-fund (deal-by-deal request rejected) | See Section 3. |
| 1026-00001 | Meridian Peak Capital Partners Fund IV, L.P. | LP counsel (Briarwood Family Office) | European / whole-fund | LPA Review Memo (Feb. 2, 2024): European structure is “favorable to BFO … relative to a deal-by-deal (American) waterfall.” Fee & Economics Memo (Feb. 4, 2024) explains the difference and notes the American waterfall “has fallen out of favor in real estate PE.” |

**Not counted:**

- **Joint ventures and club deals with sponsor promotes:** 1015-00004, 1020-00006, 1026-00004, 1036-00005, 1043-00002. These are single-project operating-company structures, not funds. None is described as an American or deal-by-deal fund waterfall.
- **Driftwood Absolute Return Fund (1024-00002):** a hedge fund with a high-water-mark incentive allocation, which is a different concept.

---

## 5. What this means for your recommendation

1. **No internal precedent.** We have no closed fund, sponsor-side LPA form or negotiation history for an American waterfall. If the client wants one, we would be drafting the deal-by-deal mechanics from scratch. That includes per-deal return of capital, allocation of write-downs and broken-deal and fund expenses to realized deals, an interim and final GP clawback, carry escrow or holdback, and guarantees.
2. **Our consistent practice and advice favor European.** Our own advice, given to both sponsors and LPs, describes the European waterfall as market-standard and LP-protective:
   - Harrowgate structuring memo and §1061 memo;
   - Meridian Peak review memos;
   - Cobalt Fund I documents.
   The §1061 memo for Harrowgate also notes that a deal-by-deal fund carries greater §1061 recharacterization risk, because carry may be distributed on each realization.
3. **Where deal-by-deal came up, it went away.**
   - Pinnacle CV: other counsel’s draft, which we replaced with a whole-fund waterfall at the client’s instruction.
   - Ridgeline-Clarion: our LP client asked for deal-by-deal carry and the sponsor refused.
   - ICM Cascadia: deal-by-deal language survives only in a single-asset co-invest side letter, where it has no economic effect, and the document has drafting problems.
4. **If the new client wants an American waterfall**, the Ironside side letter shows what to avoid. The clawback has to actually exist in the LPA, the catch-up has to be specified clearly, and every cross-reference has to be checked against the final LPA.

---

## 6. Documents relied on

**Matter 1023-00001 (Ironside / ICM Cascadia Co-Invest)**
- Engagement/engagement-letter-ironside.docx (July 14, 2022)
- Formation/side-letter-ironside-meridian-gp-execution.docx (July 29, 2022), §§3.1–3.5, 11.2
- Formation/lp-agreement-icm-co-invest-execution.docx (July 29, 2022), §§5.01–5.02, 6.02, 8.01, 10.03, 11.03, 12.09
- Formation/co-investment-allocation-agreement-execution.docx, §§7.01–7.02
- Formation/formation-governance-summary-memo.docx (July 25, 2022), §XI
- Formation/erisa-benefit-plan-investor-memo.docx (July 27, 2022), §C
- Formation/Tax/tax-structuring-analysis-memo.docx (July 20, 2022), §IV.B
- Dormancy/capital-call-suspension-notice.docx (Jan. 9, 2023)
- Correspondence/email-cross-to-calloway-wind-down-recommendation.eml (July 25, 2024)
- Dormancy K-1 and quarterly review memos; Correspondence/letter-to-bsp-reservation-of-rights.docx; Wind-Down & Reactivation/wind-down-election-right-analysis-memo.docx (for the inconsistent cross-references)

**Matter 1002-00005 (Pinnacle CV)**
- Transaction Documents/cv-lpa-tax-provisions-markup.docx (Aug. 8, 2025), §Z.1 and issues table
- Engagement/engagement-letter-pinnacle-cv-tax-structuring.docx (July 15, 2025)
- Tax Analysis/tax-structure-memorandum-pinnacle-cv.docx

**Matter 1027-00002 (Pellegrino / Ridgeline-Clarion Co-Invest)**
- Analysis & Advice/negotiation-tracker-memo.xlsx, Item 1
- Analysis & Advice/key-terms-summary-issues-memo.docx
- Transaction Documents/co-invest-lpa-execution-version.docx, §6.2 and the GP Clawback provisions

**Matter 1003-00002 (Harrowgate Fund V)**
- Structuring & Tax/fund-structuring-memo.docx (Apr. 14, 2025)
- Structuring & Tax/carried-interest-1061-memo.docx (May 5, 2025)
- Transaction Documents/lpa-offshore-feeder.docx
- Offering Documents/ppm-initial-draft.docx and ppm-revised-draft-redline.docx
- Closing/form-distribution-notice.docx
- Financing/sub-facility-term-sheet-review-memo.docx

**Matter 1004-00002 (Cobalt Life Sciences Fund I)**
- Transaction Documents/clso-fund-i-lpa-first-draft.docx, §6.2
- Transaction Documents/ppm-outline-first-draft.docx
- Structuring & Analysis/tax-structuring-memorandum.docx

**Matter 1001-00002 (Ardent Capital Partners III)**
- LP Consent & Notification/lpac-notification-and-consent-letter.docx (Feb. 5, 2024)
- LP Consent & Notification/lpac-presentation-memo.docx
- Carry & Economics/carried-interest-allocation-agreement.docx

**Matter 1002-00003 (Pinnacle Venture Fund II)**
- Closing/closing-checklist-side-letter-package.docx

**Matter 1026-00001 (Briarwood / Meridian Peak Fund IV)**
- LPA & PPM Review/lpa-review-memorandum.docx (Feb. 2, 2024)
- LPA & PPM Review/fee-economics-analysis-memo.docx (Feb. 4, 2024)
- Side-Letter Negotiation/side-letter-negotiation-strategy-memo.docx

**Matter 1041-00005 (Solara)**
- Entity Formation/lpa-master-fund-draft.docx, §6.2
- LP Communications/draft-amendment-fund-v-lpa.docx

**Caveat:** The Harrowgate memo says the European waterfall has been HCP’s practice “since HPE Fund III” (2018). The files do not show what waterfall HPE Funds I (2012) or II (2015) used, or whether we were counsel on them. If the client relationship history matters, that is worth confirming with the Harrowgate team.

<<<END OUT-0d96a0d4>>>

## Criteria

### C-001  (Agent's Output: OUT-0d96a0d4)
**No American deal-by-deal waterfall precedent**

States that no fund the firm set up uses an American, deal-by-deal distribution waterfall.
