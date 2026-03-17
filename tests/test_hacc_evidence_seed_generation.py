import unittest
from pathlib import Path
import sys
import tempfile
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from adversarial_harness.complainant import Complainant
from adversarial_harness.hacc_evidence import build_hacc_evidence_seeds, build_hacc_mediator_evidence_packet, resolve_hacc_question_evidence, _summarize_hit, _extract_source_window, _filter_section_labels_for_anchor_terms, _load_hacc_engine


class HacceEvidenceSeedGenerationTests(unittest.TestCase):
    def test_load_hacc_engine_imports_real_engine_class(self) -> None:
        engine_cls = _load_hacc_engine()

        self.assertEqual(engine_cls.__name__, "HACCResearchEngine")
        self.assertEqual(engine_cls.__module__, "hacc_research.engine")

    def test_build_hacc_evidence_seeds_includes_grounded_complainant_fields(self) -> None:
        class FakeEngine:
            def __init__(self):
                self.last_search_mode = None
                self.last_grounding_search_mode = None

            def search(self, query, top_k=3, use_vector=False, search_mode="auto"):
                self.last_search_mode = search_mode
                return {
                    "results": [
                        {
                            "document_id": "doc-1",
                            "title": "ADMINISTRATIVE PLAN",
                            "source_type": "repository_evidence",
                            "source_path": str(REPO_ROOT / "README.txt"),
                            "score": 0.91,
                            "snippet": "Residents may request an informal hearing and written notice of adverse action.",
                        }
                    ]
                }

            def build_grounding_bundle(self, query, top_k=3, claim_type="housing_discrimination", search_mode="package", use_vector=False):
                self.last_grounding_search_mode = search_mode
                return {
                    "upload_candidates": [
                        {
                            "document_id": "doc-1",
                            "title": "README.txt",
                            "relative_path": "README.txt",
                            "source_path": str(REPO_ROOT / "README.txt"),
                            "source_type": "repository_evidence",
                            "score": 0.88,
                            "snippet": "Repository evidence about grievance hearings and written notice.",
                        }
                    ],
                    "synthetic_prompts": {
                        "complaint_chatbot_prompt": "Ground the complaint chatbot in uploaded repository evidence.",
                        "mediator_evaluation_prompt": "Evaluate each uploaded evidence item.",
                    },
                    "mediator_evidence_packets": [
                        {
                            "document_label": "README.txt",
                            "source_path": str(REPO_ROOT / "README.txt"),
                            "relative_path": "README.txt",
                            "filename": "README.txt",
                            "mime_type": "text/plain",
                            "metadata": {
                                "relative_path": "README.txt",
                                "source_type": "repository_evidence",
                                "upload_strategy": "file",
                            },
                        }
                    ],
                }

            def _resolve_candidate_upload_text(self, candidate):
                return "Repository evidence about grievance hearings and written notice."

        query_specs = [
            {
                "query": "grievance hearing written notice adverse action",
                "type": "housing_discrimination",
                "category": "housing",
                "description": "Due-process complaint grounded in HACC evidence",
                "anchor_terms": ["informal hearing", "written notice", "adverse action"],
            }
        ]

        fake_engine = FakeEngine()
        with mock.patch("adversarial_harness.hacc_evidence._load_hacc_engine", return_value=lambda *args, **kwargs: fake_engine):
            seeds = build_hacc_evidence_seeds(count=1, query_specs=query_specs)

        self.assertEqual(len(seeds), 1)
        self.assertEqual(fake_engine.last_search_mode, "package")
        self.assertEqual(fake_engine.last_grounding_search_mode, "package")
        key_facts = seeds[0]["key_facts"]
        self.assertIn("repository_evidence_candidates", key_facts)
        self.assertIn("synthetic_prompts", key_facts)
        self.assertIn("mediator_evidence_packets", key_facts)
        self.assertIn("complainant_story_facts", key_facts)
        self.assertTrue(key_facts["repository_evidence_candidates"])
        self.assertTrue(key_facts["complainant_story_facts"])
        self.assertIn("complaint_chatbot_prompt", key_facts["synthetic_prompts"])
        self.assertEqual(key_facts["mediator_evidence_packets"][0]["document_text"], "Repository evidence about grievance hearings and written notice.")

    def test_resolve_hacc_question_evidence_uses_package_search_mode(self) -> None:
        class FakeEngine:
            def __init__(self):
                self.calls = []

            def search(self, query, top_k=4, use_vector=False, search_mode="auto"):
                self.calls.append(
                    {
                        "query": query,
                        "top_k": top_k,
                        "use_vector": use_vector,
                        "search_mode": search_mode,
                    }
                )
                return {
                    "results": [
                        {
                            "document_id": "doc-1",
                            "title": "ADMINISTRATIVE PLAN",
                            "source_type": "repository_evidence",
                            "source_path": str(REPO_ROOT / "README.txt"),
                            "score": 0.91,
                            "snippet": "Residents may request an informal hearing and written notice of adverse action.",
                        }
                    ]
                }

        fake_engine = FakeEngine()
        with mock.patch("adversarial_harness.hacc_evidence._get_hacc_engine_instance", return_value=fake_engine):
            payload = resolve_hacc_question_evidence(
                question="What hearing rights were denied?",
                key_facts={
                    "evidence_query": "grievance hearing written notice adverse action",
                    "anchor_terms": ["informal hearing", "written notice"],
                },
            )

        self.assertEqual(fake_engine.calls[0]["search_mode"], "package")
        self.assertIn("informal hearing", fake_engine.calls[0]["query"])
        self.assertEqual(payload["evidence_items"][0]["title"], "ADMINISTRATIVE PLAN")

    def test_complainant_prompt_prefers_grounded_case_digest(self) -> None:
        seed = {
            "type": "housing_discrimination",
            "summary": "Complaint about denied hearing rights.",
            "key_facts": {
                "incident_summary": "HACC denied a request and failed to provide hearing instructions.",
                "complainant_story_facts": [
                    "Anchor from ADMINISTRATIVE PLAN [grievance_hearing]: Residents may request an informal hearing.",
                ],
                "repository_evidence_candidates": [
                    {
                        "title": "README.txt",
                        "relative_path": "README.txt",
                        "snippet": "Repository evidence about grievance hearings.",
                    }
                ],
                "synthetic_prompts": {
                    "complaint_chatbot_prompt": "Use uploaded materials as factual grounding.",
                },
            },
            "hacc_evidence": [
                {
                    "title": "ADMINISTRATIVE PLAN",
                    "snippet": "Residents may request an informal hearing.",
                    "source_path": str(REPO_ROOT / "README.txt"),
                }
            ],
        }

        complainant = Complainant(lambda prompt: prompt, personality="detailed")
        prompt = complainant._build_complaint_prompt(seed)

        self.assertIn("Grounded complainant facts:", prompt)
        self.assertIn("Fact 1:", prompt)
        self.assertIn("Repository evidence 1:", prompt)
        self.assertIn("Prompt guidance:", prompt)

    def test_mediator_packet_prefers_repository_candidate_paths(self) -> None:
        seed = {
            "type": "housing_discrimination",
            "key_facts": {
                "evidence_query": "grievance hearing",
                "anchor_sections": ["grievance_hearing"],
                "anchor_terms": ["informal hearing"],
                "repository_evidence_candidates": [
                    {
                        "title": "README.txt",
                        "relative_path": "README.txt",
                        "source_path": str(REPO_ROOT / "README.txt"),
                        "snippet": "Repository evidence about grievance hearings.",
                    }
                ],
                "source_paths": ["/nonexistent/path.txt"],
            },
            "hacc_evidence": [],
        }

        packets = build_hacc_mediator_evidence_packet(seed, max_documents=1)

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["document_label"], "README.txt")
        self.assertEqual(packets[0]["source_path"], str(REPO_ROOT / "README.txt"))
        self.assertTrue(packets[0]["metadata"]["repository_candidate"])

    def test_mediator_packet_prefers_grounded_seed_packets(self) -> None:
        seed = {
            "type": "housing_discrimination",
            "key_facts": {
                "evidence_query": "grievance hearing",
                "mediator_evidence_packets": [
                    {
                        "document_text": "Grounded extracted evidence text",
                        "document_label": "ADMINISTRATIVE PLAN",
                        "source_path": "/tmp/policy.pdf",
                        "filename": "policy.txt",
                        "mime_type": "text/plain",
                        "metadata": {
                            "upload_strategy": "extracted_text_fallback",
                            "original_mime_type": "application/pdf",
                        },
                    }
                ],
                "repository_evidence_candidates": [
                    {
                        "title": "README.txt",
                        "relative_path": "README.txt",
                        "source_path": str(REPO_ROOT / "README.txt"),
                        "snippet": "Fallback snippet",
                    }
                ],
            },
            "hacc_evidence": [],
        }

        packets = build_hacc_mediator_evidence_packet(seed, max_documents=1)

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["document_text"], "Grounded extracted evidence text")
        self.assertEqual(packets[0]["document_label"], "ADMINISTRATIVE PLAN")
        self.assertEqual(packets[0]["metadata"]["upload_strategy"], "extracted_text_fallback")

    def test_summarize_hit_prefers_matched_rule_when_snippet_is_table_of_contents(self) -> None:
        hit = {
            "title": "ADMINISTRATIVE PLAN",
            "snippet": "14 GRIEVANCES AND APPEALS INTRODUCTION ........ 14-1 PART I: INFORMAL HEARINGS ........ 14-2",
            "matched_rules": [
                {
                    "text": "The notice must also state that the tenant may request a grievance hearing on the HACC's adverse action."
                }
            ],
        }

        summarized = _summarize_hit(hit)

        self.assertIn("tenant may request a grievance hearing", summarized["snippet"])

    def test_extract_source_window_prefers_body_paragraph_over_table_of_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "policy.txt"
            source_path.write_text(
                "Scheduling an Informal Review ........ 16-11\n"
                "Informal Review Procedures ........ 16-11\n\n"
                "Scheduling an Informal Review\n\n"
                "HACC must schedule the informal review promptly and provide written notice of the review procedures.\n",
                encoding="utf-8",
            )

            excerpt = _extract_source_window(
                source_path=str(source_path),
                anchor_terms=["Scheduling an Informal Review"],
                fallback_snippet="Scheduling an Informal Review ........ 16-11",
            )

        self.assertIn("HACC must schedule the informal review promptly", excerpt)
        self.assertNotIn("........ 16-11", excerpt)

    def test_extract_source_window_prefers_substantive_policy_text_when_heading_repeat_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "policy.txt"
            source_path.write_text(
                "Administrative Plan - Table of Contents\n\n"
                "16-III.B. Informal Reviews ........ 16-11\n"
                "Scheduling an Informal Review ........ 16-11\n"
                "Informal Review Procedures ........ 16-11\n\n"
                "The notice must describe how to obtain the informal review.\n\n"
                "Scheduling an Informal Review\n\n"
                "HACC Policy\n\n"
                "A request for an informal review must be made in writing and delivered to HACC.\n"
                "HACC must schedule and send written notice of the informal review within 10 business days.\n",
                encoding="utf-8",
            )

            excerpt = _extract_source_window(
                source_path=str(source_path),
                anchor_terms=["Scheduling an Informal Review"],
                fallback_snippet="Scheduling an Informal Review ........ 16-11",
            )

        self.assertIn("HACC Policy", excerpt)
        self.assertIn("must schedule and send written notice", excerpt)
        self.assertNotIn("Table of Contents", excerpt)

    def test_extract_source_window_carries_definitions_into_due_process_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "policy.txt"
            source_path.write_text(
                "I. Definitions applicable to the grievance procedure [24 CFR 966.53]\n\n"
                "A. Grievance: Any dispute a tenant may have with respect to HACC action or failure to act in accordance with the individual tenant's lease or HACC regulations that adversely affects the individual tenant's rights, duties, welfare, or status.\n\n"
                "B. Complainant: Any tenant whose grievance is presented to HACC.\n\n"
                "C. Elements of due process: An eviction action or a termination of tenancy in a state or local court in which adequate notice and an opportunity to refute the evidence are required.\n",
                encoding="utf-8",
            )

            excerpt = _extract_source_window(
                source_path=str(source_path),
                anchor_terms=["Definitions applicable to the grievance procedure"],
                fallback_snippet="Grievance: Any dispute a tenant may have with respect to HACC action or failure to",
                window_chars=900,
            )

        self.assertIn("A. Grievance:", excerpt)
        self.assertIn("C. Elements of due process:", excerpt)

    def test_extract_source_window_prefers_excerpt_with_more_anchor_term_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "policy.txt"
            source_path.write_text(
                "The authority must safeguard the due process rights of applicants and tenants before denying admission.\n\n"
                "Grievance Hearing Procedures\n\n"
                "A tenant may request an informal hearing through the grievance process, and HACC must provide written notice of the hearing decision.\n",
                encoding="utf-8",
            )

            excerpt = _extract_source_window(
                source_path=str(source_path),
                anchor_terms=["grievance", "hearing", "appeal", "informal hearing", "due process"],
                fallback_snippet="The authority must safeguard the due process rights of applicants and tenants before denying admission.",
            )

        self.assertIn("request an informal hearing", excerpt)
        self.assertIn("grievance process", excerpt)
        self.assertIn("due process rights", excerpt)
        self.assertLess(excerpt.lower().find("request an informal hearing"), excerpt.lower().rfind("hearing decision") + 1)

    def test_extract_source_window_prefers_admin_plan_notice_body_over_toc_heading_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "admin-plan.txt"
            source_path.write_text(
                "16-11 Notice to the Applicant [24 CFR 982.554(a)] ........ 16-11 "
                "Scheduling an Informal Review ........ 16-11 "
                "Informal Review Procedures [24 CFR 982.554(b)] ........ 16-11 "
                "Informal Review Decision [24 CFR 982.554(b)] ........ 16-15\n\n"
                "Notice to the Applicant [24 CFR 982.554(a)]\n\n"
                "HACC must give an applicant prompt notice of a decision denying assistance. "
                "The notice must state that the applicant may request an informal review and describe how to obtain it.\n\n"
                "Scheduling an Informal Review\n\n"
                "HACC Policy\n\n"
                "A request for an informal review must be made in writing and delivered to HACC. "
                "HACC must schedule and send written notice of the informal review within 10 business days.\n",
                encoding="utf-8",
            )

            excerpt = _extract_source_window(
                source_path=str(source_path),
                anchor_terms=[
                    "Notice to the Applicant",
                    "Scheduling an Informal Review",
                    "Informal Review Procedures",
                    "Informal Review Decision",
                ],
                fallback_snippet="Notice to the Applicant",
            )

        self.assertIn("prompt notice of a decision denying assistance", excerpt)
        self.assertIn("must schedule and send written notice", excerpt)
        self.assertNotIn("........ 16-11", excerpt)

    def test_extract_source_window_prefers_knowledge_graph_text_before_raw_blob(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            hacc_root = repo_root / "hacc_website"
            knowledge_root = hacc_root / "knowledge_graph" / "texts"
            knowledge_root.mkdir(parents=True)

            source_path = hacc_root / "policy-id"
            source_path.write_bytes(b"\x00\x01\x02" * 50000)
            (knowledge_root / "policy-id.txt").write_text(
                "Scheduling an Informal Review\n\n"
                "HACC must schedule the informal review promptly and provide written notice.\n",
                encoding="utf-8",
            )

            with mock.patch("adversarial_harness.hacc_evidence._repo_root", return_value=repo_root):
                excerpt = _extract_source_window(
                    source_path=str(source_path),
                    anchor_terms=["Scheduling an Informal Review"],
                    fallback_snippet="Scheduling an Informal Review ........ 16-11",
                )

        self.assertIn("HACC must schedule the informal review promptly", excerpt)
        self.assertNotIn("........ 16-11", excerpt)

    def test_filter_section_labels_drops_unrequested_anchor_classes(self) -> None:
        labels = _filter_section_labels_for_anchor_terms(
            ["grievance_hearing", "appeal_rights", "reasonable_accommodation", "adverse_action"],
            ["grievance", "hearing", "appeal", "informal hearing", "due process", "adverse action"],
        )

        self.assertEqual(labels, ["grievance_hearing", "appeal_rights", "adverse_action"])


if __name__ == "__main__":
    unittest.main()
