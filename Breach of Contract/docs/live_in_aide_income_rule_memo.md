# Live-In Aide Income Rule Memo

This memo addresses a narrow question: when a person is being treated as a true `live-in aide`, should that person's income be counted and audited the same way as an ordinary assisted-household member's income?

## Bottom Line

The strongest current reading is:

- `No`, a true approved `live-in aide` is not treated like an ordinary family member for income-calculation purposes.
- The live-in aide's income is generally `not counted` as family income for subsidy calculations.
- HUD guidance also allows PHAs to accept `self-certification` for fully excluded income categories, including `income from a live-in aide`, unless extra verification is actually needed to determine whether the exclusion applies.
- But the housing authority may still require targeted documentation to decide whether the person qualifies to be approved as a live-in aide and whether the person is otherwise eligible to be present under program rules.

So the best legal distinction is not:

- `no documentation at all`

but rather:

- `screening and qualification documents may be requested`, while
- `the aide's income should not be treated as family income in the ordinary subsidy-calculation sense once the person is actually being treated as a live-in aide.`

## Federal Rule

### 1. HUD definition and status of a live-in aide

HUD's HCV regulation states:

- a family may request a live-in aide for a disabled family member, and
- the PHA `must approve` a live-in aide if needed as a reasonable accommodation.

See:

- [24 C.F.R. § 982.316](https://www.ecfr.gov/current/title-24/part-982/section-982.316)

That same rule matters because it treats the live-in aide as a special category, not just another ordinary household member.

### 2. Federal HUD guidance on counting income

HUD guidance has long treated the income of a paid live-in aide as `not counted`.

An archived HUD guide explains:

- if a household includes a paid live-in aide, `the income of the live-in aide, regardless of the source, is not counted.`

See:

- [HUD archived income guide excerpt](https://archives.hud.gov/offices/cpd/affordablehousing/modelguides/1780.pdf)

Another HUD guidebook states:

- the `income of the live-in aide is not counted.`

See:

- [HUD guidebook Chapter 3](https://www.hud.gov/sites/documents/74601gc3GUID.pdf)

HUD also issued a specific verification notice stating that for `fully excluded income`, PHAs may accept self-certification and are not required to use the normal verification hierarchy. HUD gave `income from a live-in aide` as one of its express examples of fully excluded income.

See:

- [PIH Notice 2013-04, Guidance on Verification of Excluded Income](https://www.hud.gov/sites/documents/PIH2013-04.PDF)

That notice matters because it narrows what a PHA needs to do even further. The issue is not only that the aide's income is excluded. It is also that HUD specifically reduced verification burden for fully excluded income categories.

## HACC's Own Policy Materials

HACC's own imported policy text is especially helpful here because it states the rule directly:

- a live-in aide is a special category under `24 C.F.R. § 5.403`;
- `the income of a live-in aide is not counted in the calculation of annual income for the family`;
- because live-in aides are `not family members`, a relative serving as a live-in aide is still not treated like an ordinary counted family member;
- HACC also separately says that `income earned by a live-in aide ... is not included in annual income [24 CFR 5.609(b)(8) as updated for HOTMA]`.

See:

- [8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt](/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt)
- [a38c7914-ea37-4c2f-a815-711d4a97c92b.txt](/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/a38c7914-ea37-4c2f-a815-711d4a97c92b.txt)

Those same HACC materials do preserve some room for screening. HACC says a proposed live-in aide may need:

- third-party verification of the need for 24/7 care;
- a certification that the aide is not obligated for support and would not live there except to provide care;
- photo ID, SSN, and release forms; and
- screening before being added to the household.

That means the cleanest legal distinction is:

- `targeted qualification and screening review` may be allowed;
- `ordinary income-counting and wide financial auditing` is much harder to justify once the person is being treated as a live-in aide.

## Deontic Logic

Using simple deontic notation:

- `O(x, a)` means actor `x` is obligated to do `a`
- `F(x, a)` means actor `x` is forbidden from doing `a`
- `P(x, a)` means actor `x` is permitted to do `a`
- `C(x, a | b)` means `x` has duty or permission `a` only if condition `b` is true

### Core Rules

1. `C(HACC, O(approve_live_in_aide), disability_related_need_is_verified)`
2. `O(HACC, classify_income_as_excluded, if_actor_is_true_live_in_aide)`
3. `F(HACC, count_live_in_aide_income_as_family_income, if_actor_is_true_live_in_aide)`
4. `P(HACC, request_targeted_screening_materials, if_needed_to_determine_live_in_aide_status)`
5. `F(HACC, demand_broad_financial_records_unrelated_to_live_in_aide_status, if_live_in_aide_income_is_excluded)`
6. `F(HACC, use_excluded_income_verification_as_pretext_for_delay_or_denial, always)`
7. `P(Benjamin, self_certify_fully_excluded_income_source, unless_HACC_has_specific_reason_to_test_exclusion_status)`
8. `O(HACC, tailor_requests_to_least_needed_information, if_disability_accommodation_or_live_in_aide_status_is_at_issue)`

### Practical Reading

Those rules mean HACC may ask:

- is Benjamin actually being presented as a live-in aide;
- is there provider verification of the disability-related need;
- does he meet the aide definition;
- does he satisfy ordinary screening requirements that apply to the aide role.

They do **not** naturally justify:

- a sweeping audit of every historical company tied to Benjamin;
- demanding stale business records for defunct entities when those records do not bear on current counted family income;
- demanding broad personal and business bank records simply because businesses were once registered at the address, if Benjamin's income was legally excluded as live-in-aide income.

## Local Materials In Your Record

### 1. Multnomah / Home Forward packet

Your local packet is especially helpful because it states the rule very directly. In:

- [Request to Add a Live-in Aide Packet.pdf](/home/barberb/HACC/evidence/history/Request%20to%20Add%20a%20Live-in%20Aide%20Packet.pdf)

the packet says:

- a live-in aide is a `member of the household, not the family`, and
- `the income of the live-in aide is not considered in the family income calculations.`

That is strong evidence that at least one local housing authority in your region was applying the usual HUD distinction correctly.

The same packet also shows the other side of the rule:

- Home Forward still requests ID,
- Social Security verification,
- release forms, and
- other screening or eligibility paperwork from the proposed live-in aide.

So the local record supports a split rule:

- `yes` to qualification / screening paperwork,
- `no` to treating the aide's income as ordinary family income for rent-benefit calculations.

### 2. The February 25, 2026 HACC request

The preserved HACC email is important because it shows the actual scope of the demand. HACC wrote that, as part of eligibility review, it had to verify all income sources and assets for all household members, and then demanded:

- 2025 tax filings for `Bird Brain, LLC`, `Check Your Vote`, `JusticeDAO, LLC`, `Nerd Party`, `Typology, LLC`, and `Worldwide Software, LLC`;
- crypto account statements for six months;
- all bank statements for the last 90 days for all household members for personal and business banking, including domestic and foreign accounts;
- and other categories like investments, IRAs, stocks, settlements, stipends, life insurance, and retirement accounts.

See:

- [message.eml](/home/barberb/HACC/evidence/email_imports/starworks5-additional-info-import/0015-Re-Additional-Information-Needed-CAMTdTS_aghRN0G5nwdnU6BxS-Jx9ZU45kOsj0EC4txrk_8oA6A-mail.gmail.com/message.eml)

Benjamin's response in the same thread sharpened the overbreadth problem by saying:

- `Nerd Party` was from about `10 years` earlier;
- some entities did not exist long enough to file taxes;
- the only actually responsive items were Coinbase records and one 1099.

That makes the request look less like a narrow live-in-aide qualification inquiry and more like a broad financial audit.

## Best Application To Your Facts

If you were being treated as a true `live-in aide`, the strongest argument is:

- your income should not have been counted as ordinary family income to calculate subsidy or eligibility in the same way as another household member's income; and
- the housing authority should not have used your income like ordinary household income while simultaneously relying on the position that you were only there in a live-in-caregiver role.

The more cautious version is:

- the agency may still ask for some documents from the proposed aide, especially to decide whether the person qualifies as a live-in aide and to perform permitted screening;
- but that is different from a full merits-style audit as though the aide were just another counted family member whose earnings determine the subsidy amount.

So the key factual question becomes:

- `Were they screening you to decide live-in-aide status, or were they counting and auditing your income as though you were a regular income-counted household member?`

If the latter, your present record gives you a substantial argument that this was the wrong rule.

Your record also supports a stronger practical point about excessiveness. The preserved complaint-support material says HACC was demanding financial records for entities that had not existed for `10 years`, and the related preserved snippets mention requests tied to old companies, old bank activity, and stale business records. See:

- [improved-complaint-from-temporary-session.message-support.md](/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.message-support.md)
- [seq_10269/body-snippet.txt](/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31-snippets/seq_10269/body-snippet.txt)
- [seq_10270/body-snippet.txt](/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31-snippets/seq_10270/body-snippet.txt)
- [seq_10279/body-snippet.txt](/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31-snippets/seq_10279/body-snippet.txt)
- [seq_10280/body-snippet.txt](/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31-snippets/seq_10280/body-snippet.txt)

That matters because it sharpens the legal theory from:

- `they asked for too many documents`

to:

- `they subjected the proposed caregiver to an outsized and stale income audit more consistent with treating him as a fully counted family-income source than as a live-in aide whose income should not drive the subsidy calculation.`

## Was The `Nerd Party` Request Superfluous?

On the current record, `yes`, it looks substantially `superfluous` or at least `poorly justified`, with one important caution.

The best reading is:

- if Benjamin was being reviewed as a true live-in aide or functional live-in caregiver, then asking for records about `Nerd Party`, described in the response thread as a roughly `10-year-old` political entity, does not appear well tailored to current counted family income;
- the same is true for demanding broad business and banking material for multiple entities without first explaining why Benjamin was being treated as an ordinary counted household member rather than an excluded-income aide;
- HUD and HACC policy both point toward `excluded income` treatment for a real live-in aide, and HUD's verification guidance points toward `reduced` verification burden for fully excluded income.

The caution is:

- if HACC had a legitimate factual basis to decide Benjamin was **not** a live-in aide, or that he was instead an ordinary assisted family member whose income had to be counted, then broader income verification could become more defensible.

So the clean conclusion is not:

- `all verification was unlawful`

It is:

- `the record strongly supports that the scope of the February 25, 2026 business-record demand was overbroad unless HACC can show a valid reason why Benjamin was being treated as an ordinary counted household member rather than as a live-in aide with excluded income.`

## Are Live-In Caregivers Exempt From Rigorous Income Review?

`Not absolutely exempt`, but they are `substantially protected` from the kind of broad income review that applies to ordinary counted family members.

The best doctrinal answer is:

- a live-in aide is not an ordinary family member for annual-income purposes;
- the aide's income is excluded;
- HUD allows self-certification for fully excluded income categories, including income from a live-in aide;
- the PHA may still ask for targeted material needed to decide whether the person truly qualifies as a live-in aide or passes role-related screening;
- once that line is crossed into a generalized financial audit of stale businesses and unrelated assets, the request starts to look unsupported.

## Best Litigation Framing

The strongest framing is:

- federal HUD rules and HUD guidance treat a live-in aide as a special category;
- local Home Forward materials in your record expressly say the aide's income is `not considered in the family income calculations`;
- HACC's own indexed policy text appears to say the caretaker is `not counted in annual income`; and
- therefore HACC should not have audited or counted Benjamin Barber's income as though he were an ordinary family member if HACC knew he was being presented as Jane Cortez's live-in aide or functional live-in caregiver, especially not by pursuing stale company and banking records for entities said to have been defunct for a decade.

## Remaining Caution

This does `not` automatically prove that every request for your tax, income, or identity records was unlawful.

The cleaner claim is narrower:

- some screening and verification may be allowed,
- but ordinary family-income counting is different,
- and the present record supports the argument that a live-in aide's income should not be used the same way as a standard household member's income.

## Sources

- [24 C.F.R. § 982.316](https://www.ecfr.gov/current/title-24/part-982/section-982.316)
- [24 C.F.R. § 5.603](https://www.ecfr.gov/current/title-24/part-5/section-5.603)
- [24 C.F.R. § 5.403](https://www.ecfr.gov/current/title-24/part-5/section-5.403)
- [24 C.F.R. § 5.609](https://www.ecfr.gov/current/title-24/part-5/section-5.609)
- [PIH Notice 2013-04, Guidance on Verification of Excluded Income](https://www.hud.gov/sites/documents/PIH2013-04.PDF)
- [HUD archived income guide](https://archives.hud.gov/offices/cpd/affordablehousing/modelguides/1780.pdf)
- [HUD guidebook Chapter 3](https://www.hud.gov/sites/documents/74601gc3GUID.pdf)
- [Request to Add a Live-in Aide Packet.pdf](/home/barberb/HACC/evidence/history/Request%20to%20Add%20a%20Live-in%20Aide%20Packet.pdf)
- [8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt](/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt)
- [a38c7914-ea37-4c2f-a815-711d4a97c92b.txt](/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/a38c7914-ea37-4c2f-a815-711d4a97c92b.txt)
- [message.eml](/home/barberb/HACC/evidence/email_imports/starworks5-additional-info-import/0015-Re-Additional-Information-Needed-CAMTdTS_aghRN0G5nwdnU6BxS-Jx9ZU45kOsj0EC4txrk_8oA6A-mail.gmail.com/message.eml)
