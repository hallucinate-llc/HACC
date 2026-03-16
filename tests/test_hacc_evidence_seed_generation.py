import unittest
from pathlib import Path
import sys
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from adversarial_harness.complainant import Complainant
from adversarial_harness.hacc_evidence import build_hacc_evidence_seeds, build_hacc_mediator_evidence_packet


class HacceEvidenceSeedGenerationTests(unittest.TestCase):
    def test_build_hacc_evidence_seeds_includes_grounded_complainant_fields(self) -> None:
        class FakeEngine:
            def search(self, query, top_k=3, use_vector=False):
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

            def build_grounding_bundle(self, query, top_k=3, claim_type="housing_discrimination", use_vector=False):
                return {
                    "upload_candidates": [
                        {
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
                }

        query_specs = [
            {
                "query": "grievance hearing written notice adverse action",
                "type": "housing_discrimination",
                "category": "housing",
                "description": "Due-process complaint grounded in HACC evidence",
                "anchor_terms": ["informal hearing", "written notice", "adverse action"],
            }
        ]

        with mock.patch("adversarial_harness.hacc_evidence._load_hacc_engine", return_value=FakeEngine):
            seeds = build_hacc_evidence_seeds(count=1, query_specs=query_specs)

        self.assertEqual(len(seeds), 1)
        key_facts = seeds[0]["key_facts"]
        self.assertIn("repository_evidence_candidates", key_facts)
        self.assertIn("synthetic_prompts", key_facts)
        self.assertIn("complainant_story_facts", key_facts)
        self.assertTrue(key_facts["repository_evidence_candidates"])
        self.assertTrue(key_facts["complainant_story_facts"])
        self.assertIn("complaint_chatbot_prompt", key_facts["synthetic_prompts"])

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


if __name__ == "__main__":
    unittest.main()
