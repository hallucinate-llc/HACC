#!/usr/bin/env bash
set -euo pipefail

out_dir="/home/barberb/HACC/workspace/exhibit_cover_pages/supplemental_background_appendix"
mkdir -p "$out_dir"

cat > "$out_dir/README.md" <<'EOF'
# Supplemental Background Appendix Exhibit Cover Pages

This directory contains the completed:

1. `tab cover page`; and
2. `exhibit cover page`

for each `Exhibit A-*` and `Exhibit B-*` item in the supplemental background appendix.

Use with:

- [128_supplemental_background_appendix_exhibit_letter_schedule_2026-04-08.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/128_supplemental_background_appendix_exhibit_letter_schedule_2026-04-08.md)
- [127_supplemental_background_appendix_print_order_2026-04-08.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/127_supplemental_background_appendix_print_order_2026-04-08.md)

Completed exhibits:

- `Exhibit A-1` through `Exhibit A-20`
- `Exhibit B-1` through `Exhibit B-14`
EOF

make_pair() {
  local label="$1"
  local section="$2"
  local title="$3"
  local source="$4"
  local status="$5"
  local notes="$6"
  local relied="$7"
  local props="$8"
  local foundation="$9"
  local limitation="${10}"
  local slug="${11}"

  cat > "$out_dir/${slug}_tab_cover_page.md" <<EOF
# Exhibit Tab Cover Page

\`EXHIBIT LABEL\`

\`${label}\`

\`SECTION\`

\`${section}\`

\`SHORT TITLE\`

\`${title}\`

\`SOURCE FILE\`

\`${source}\`

\`STATUS\`

\`${status}\`

\`NOTES\`

\`${notes}\`
EOF

  cat > "$out_dir/${slug}_cover_page.md" <<EOF
# Exhibit Cover Page

\`EXHIBIT LABEL\`

\`${label}\`

\`SHORT TITLE\`

\`${title}\`

\`SOURCE FILE\`

\`${source}\`

\`RELIED ON BY\`

${relied}

\`PROPOSITION(S) THIS EXHIBIT IS OFFERED TO SUPPORT\`

${props}

\`AUTHENTICITY / FOUNDATION NOTE\`

\`${foundation}\`

\`LIMITATION NOTE\`

\`${limitation}\`
EOF
}

relied_common='1. [declaration_of_benjamin_barber_re_technology_and_computational_law_background_2026-04-08.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/declaration_of_benjamin_barber_re_technology_and_computational_law_background_2026-04-08.md)
2. [04_declaration_of_benjamin_barber_in_support_of_motions_final.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/04_declaration_of_benjamin_barber_in_support_of_motions_final.md) as background and credibility support'

make_pair "Exhibit A-1" "Supplemental background appendix" "2014 assistive technology concept" "/home/barberb/HACC/evidence/paper documents/assistive technology 2014.pdf" "True copy" "Early assistive-technology concept exhibit." "$relied_common" "1. Early 2014 assistive AR/VR goggles concept work existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support, not a housing-liability record." "exhibit_A_1"
make_pair "Exhibit A-2" "Supplemental background appendix" "2014 assistive interface support" "/home/barberb/HACC/evidence/paper documents/assistive technology 2.pdf" "True copy" "Additional assistive-interface support exhibit." "$relied_common" "1. Additional 2014 assistive-interface development support existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support, not a housing-liability record." "exhibit_A_2"
make_pair "Exhibit A-3" "Supplemental background appendix" "Hallucinate LLC / Meta grant submission" "/home/barberb/HACC/evidence/paper documents/Submission_ Hallucinate LLC.pdf" "True copy" "Meta AI Glasses grant and Hallucinate LLC continuity exhibit." "$relied_common" "1. Meta glasses grant submission and Hallucinate LLC / InfiniEdge continuity existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_3"
make_pair "Exhibit A-4" "Supplemental background appendix" "Lift coding repository exhibit" "/home/barberb/HACC/evidence/paper documents/endomorphosis_lift_coding_ when you need to code like you're iron man.pdf" "True copy" "Hands-free and immersive coding exhibit." "$relied_common" "1. Hands-free and immersive coding repository work existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_4"
make_pair "Exhibit A-5" "Supplemental background appendix" "InfiniEdge governance exhibit" "/home/barberb/HACC/evidence/paper documents/Re_ InifiniEdge AI Release 3.0 Votes seeking!.pdf" "True copy" "InfiniEdge AI governance and TSC exhibit." "$relied_common" "1. InfiniEdge AI governance and TSC role support existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_5"
make_pair "Exhibit A-6" "Supplemental background appendix" "Be My Eyes / Ray-Ban Meta context" "/home/barberb/HACC/evidence/paper documents/Be My Eyes on Ray-Ban Meta Glasses - Hands-Free Visual Assistance.pdf" "True copy" "Ray-Ban Meta visual-assistance platform context exhibit." "$relied_common" "1. Ray-Ban Meta and visual-assistance platform context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit provides technology context rather than direct housing proof." "exhibit_A_6"
make_pair "Exhibit A-7" "Supplemental background appendix" "BUD-E education exhibit" "/home/barberb/HACC/evidence/paper documents/BUD-E AI-Assisted Education for All.pdf" "True copy" "AI education and research-work continuity exhibit." "$relied_common" "1. AI education and related LAION / Intel-linked work existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_7"
make_pair "Exhibit A-8" "Supplemental background appendix" "Navi exhibit one" "/home/barberb/HACC/evidence/paper documents/navi teacher april 2025 .png" "True copy" "Navi education-software exhibit." "$relied_common" "1. The Navi education-software line existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_8"
make_pair "Exhibit A-9" "Supplemental background appendix" "Navi exhibit two" "/home/barberb/HACC/evidence/paper documents/navi teacher 2.png" "True copy" "Additional Navi support exhibit." "$relied_common" "1. Additional Navi education-software support existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_9"
make_pair "Exhibit A-10" "Supplemental background appendix" "Computational neuroscience exhibit" "/home/barberb/HACC/evidence/paper documents/Benjamin Barber computational neuroscience.png" "True copy" "Computational neuroscience tooling exhibit." "$relied_common" "1. Computational-neuroscience repository work existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_10"
make_pair "Exhibit A-11" "Supplemental background appendix" "Protein folding exhibit" "/home/barberb/HACC/evidence/paper documents/Benjamin Barber protein folding.png" "True copy" "Protein-design and biochemistry exhibit." "$relied_common" "1. Protein-design and biochemistry repository work existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_11"
make_pair "Exhibit A-12" "Supplemental background appendix" "Logic synthesis exhibit" "/home/barberb/HACC/evidence/paper documents/Benjamin Barber Logic Synthesis.pdf" "True copy" "Logic and theorem-prover exhibit." "$relied_common" "1. Logic, theorem-prover, and computational-law tooling existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_12"
make_pair "Exhibit A-13" "Supplemental background appendix" "Legal scraper infrastructure exhibit" "/home/barberb/HACC/evidence/paper documents/ipfs_datasets_py_ipfs_datasets_py_processors_legal_scrapers at main · endomorphosis_ipfs_datasets_py.pdf" "True copy" "Legal-source scraping and ingestion infrastructure exhibit." "$relied_common" "1. Legal-source scraping and ingestion infrastructure existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_13"
make_pair "Exhibit A-14" "Supplemental background appendix" "JusticeDAO exhibit" "/home/barberb/HACC/evidence/paper documents/benjamin barber justice DAO.pdf" "True copy" "JusticeDAO legal-source indexing exhibit." "$relied_common" "1. JusticeDAO legal-source indexing and search infrastructure existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_14"
make_pair "Exhibit A-15" "Supplemental background appendix" "Stanford deontic logic outreach" "/home/barberb/HACC/evidence/paper documents/Gmail - Deontic Logic and Legal systems.pdf" "True copy" "Stanford outreach on deontic logic and legal systems." "$relied_common" "1. Stanford outreach on deontic logic and legal systems existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_15"
make_pair "Exhibit A-16" "Supplemental background appendix" "Stanford CodeX exhibit" "/home/barberb/HACC/evidence/paper documents/Benjamin Barber Stanford Codex Law School .png" "True copy" "Stanford CodeX participation exhibit." "$relied_common" "1. Stanford CodeX meeting participation context existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_16"
make_pair "Exhibit A-17" "Supplemental background appendix" "Stanford FutureLaw exhibit" "/home/barberb/HACC/evidence/paper documents/Home - CodeX FutureLaw.pdf" "True copy" "Stanford FutureLaw programming exhibit." "$relied_common" "1. Stanford FutureLaw programming context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background support rather than primary proof of any housing event." "exhibit_A_17"
make_pair "Exhibit A-18" "Supplemental background appendix" "Reserved Grok skill-assessment summary" "Reserved: Grok skill-assessment summary" "Reserved demonstrative" "Reserved supplemental demonstrative placeholder." "$relied_common" "1. Reserved for a supplemental machine-generated demonstrative, if actually added later." "Use only if the reserved demonstrative file is actually created and inserted into the appendix." "Reserved demonstrative only; not current primary proof and not yet an underlying repository exhibit file." "exhibit_A_18"
make_pair "Exhibit A-19" "Supplemental background appendix" "Reserved ChatGPT skill-assessment summary" "Reserved: ChatGPT skill-assessment summary" "Reserved demonstrative" "Reserved supplemental demonstrative placeholder." "$relied_common" "1. Reserved for a supplemental machine-generated demonstrative, if actually added later." "Use only if the reserved demonstrative file is actually created and inserted into the appendix." "Reserved demonstrative only; not current primary proof and not yet an underlying repository exhibit file." "exhibit_A_19"
make_pair "Exhibit A-20" "Supplemental background appendix" "Reserved Google Search skill-assessment summary" "Reserved: Google Search skill-assessment summary" "Reserved demonstrative" "Reserved supplemental demonstrative placeholder." "$relied_common" "1. Reserved for a supplemental public-summary demonstrative, if actually added later." "Use only if the reserved demonstrative file is actually created and inserted into the appendix." "Reserved demonstrative only; not current primary proof and not yet an underlying repository exhibit file." "exhibit_A_20"

make_pair "Exhibit B-1" "Supplemental background appendix" "Waterleaf application exhibit" "/home/barberb/HACC/evidence/paper documents/waterleaf_application.png" "True copy" "Waterleaf relocation and backup-plan exhibit." "$relied_common" "1. The Waterleaf relocation and backup-plan route existed." "Use as a repository-preserved image exhibit from the paper-documents set." "This exhibit supports background location and backup-plan context, not by itself the full portability handling chain." "exhibit_B_1"
make_pair "Exhibit B-2" "Supplemental background appendix" "Waterleaf to Moody corridor map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to 3338 S Moody Ave, Portland, OR 97239 - Google Maps.pdf" "True copy" "Waterleaf proximity to the OHSU and Moody corridor." "$relied_common" "1. Waterleaf was proximate to the OHSU and Moody corridor." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_2"
make_pair "Exhibit B-3" "Supplemental background appendix" "Waterleaf to OTRADI map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to OTRADI - Google Maps.pdf" "True copy" "Waterleaf proximity to OTRADI." "$relied_common" "1. Waterleaf was proximate to OTRADI." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_3"
make_pair "Exhibit B-4" "Supplemental background appendix" "Waterleaf to innovation hub map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to Metro Region Innovation Hub - Google Maps.pdf" "True copy" "Waterleaf proximity to research and innovation infrastructure." "$relied_common" "1. Waterleaf was proximate to research and innovation infrastructure." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_4"
make_pair "Exhibit B-5" "Supplemental background appendix" "Waterleaf to Safeway map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to Safeway - Google Maps.pdf" "True copy" "Waterleaf grocery-accessibility exhibit." "$relied_common" "1. Waterleaf had grocery accessibility." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_5"
make_pair "Exhibit B-6" "Supplemental background appendix" "Waterleaf to St. James Lutheran Church map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to St. James Lutheran Church - Google Maps.pdf" "True copy" "Waterleaf church-accessibility exhibit." "$relied_common" "1. Waterleaf had church accessibility." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_6"
make_pair "Exhibit B-7" "Supplemental background appendix" "Waterleaf to library map" "/home/barberb/HACC/evidence/paper documents/Waterleaf to Multnomah County Central Library - Google Maps.pdf" "True copy" "Waterleaf library-accessibility exhibit." "$relied_common" "1. Waterleaf had library accessibility." "Use as a repository-preserved map exhibit from the paper-documents set." "This exhibit is geographic context rather than direct proof of portability processing." "exhibit_B_7"
make_pair "Exhibit B-8" "Supplemental background appendix" "OHSU rehabilitation exhibit" "/home/barberb/HACC/evidence/paper documents/Physical and Occupational Rehabilitation Near You _ OHSU.pdf" "True copy" "OHSU rehabilitation services exhibit." "$relied_common" "1. OHSU rehabilitation proximity and support context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background location and service context rather than direct portability proof." "exhibit_B_8"
make_pair "Exhibit B-9" "Supplemental background appendix" "OHSU fitness center exhibit" "/home/barberb/HACC/evidence/paper documents/Certified Medical Fitness Center _ OHSU.pdf" "True copy" "OHSU wellness and fitness context exhibit." "$relied_common" "1. OHSU wellness, pool, and fitness context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background location and service context rather than direct portability proof." "exhibit_B_9"
make_pair "Exhibit B-10" "Supplemental background appendix" "March Wellness contact exhibit" "/home/barberb/HACC/evidence/paper documents/Contact March Wellness _ OHSU.pdf" "True copy" "March Wellness access and contact exhibit." "$relied_common" "1. March Wellness access and contact context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background location and service context rather than direct portability proof." "exhibit_B_10"
make_pair "Exhibit B-11" "Supplemental background appendix" "OHSU FAQ exhibit" "/home/barberb/HACC/evidence/paper documents/FAQ _ OHSU.pdf" "True copy" "OHSU facility support exhibit." "$relied_common" "1. OHSU facility support context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background location and service context rather than direct portability proof." "exhibit_B_11"
make_pair "Exhibit B-12" "Supplemental background appendix" "OHSU team exhibit" "/home/barberb/HACC/evidence/paper documents/Team Members _ OHSU.pdf" "True copy" "OHSU team and services exhibit." "$relied_common" "1. OHSU team and services context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background location and service context rather than direct portability proof." "exhibit_B_12"
make_pair "Exhibit B-13" "Supplemental background appendix" "OBI pre-application exhibit" "/home/barberb/HACC/evidence/paper documents/Gmail - OBI Pre-application.pdf" "True copy" "OBI wet-lab planning contact exhibit." "$relied_common" "1. OBI pre-application and wet-lab planning contact existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is background work-location context rather than direct portability proof." "exhibit_B_13"
make_pair "Exhibit B-14" "Supplemental background appendix" "TriMet LIFT exhibit" "/home/barberb/HACC/evidence/paper documents/lift service.pdf" "True copy" "TriMet LIFT service and budget-pressure exhibit." "$relied_common" "1. TriMet LIFT budget, service-adjustment, and LIFT+ with Uber context existed." "Use as a repository-preserved documentary exhibit from the paper-documents set." "This exhibit is transportation-context support rather than direct portability proof." "exhibit_B_14"
