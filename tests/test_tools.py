"""Input/output shape tests for each tool. Deterministic, no network."""

from __future__ import annotations

import pytest

from src.tools import ethics, eu_ai_act, memo, mitre_atlas, nist_rmf


class TestNistRmf:
    def test_returns_matches_key(self):
        result = nist_rmf.lookup("security")
        assert "matches" in result
        assert isinstance(result["matches"], list)
        assert "source_url" in result

    def test_match_shape(self):
        result = nist_rmf.lookup("security")
        assert result["matches"], "expected at least one match for 'security'"
        for m in result["matches"]:
            assert set(m) >= {"function", "category", "subcategory", "text", "guidance"}

    def test_empty_query_returns_all(self):
        result = nist_rmf.lookup("")
        assert len(result["matches"]) >= 10

    def test_multi_term_query_is_intersection(self):
        # Both terms must appear in the entry
        result = nist_rmf.lookup("security cybersecurity")
        assert len(result["matches"]) >= 1


class TestMitreAtlas:
    def test_returns_matches_key(self):
        result = mitre_atlas.lookup("prompt injection")
        assert "matches" in result
        assert result["matches"]

    def test_match_shape_for_technique(self):
        result = mitre_atlas.lookup("AML.T0051")
        assert result["matches"]
        m = result["matches"][0]
        assert m["id"] == "AML.T0051"
        assert m["type"] == "technique"
        assert "name" in m and "tactic" in m and "description" in m

    def test_match_shape_for_mitigation(self):
        result = mitre_atlas.lookup("AML.M0015")
        assert result["matches"]
        m = result["matches"][0]
        assert m["id"] == "AML.M0015"
        assert m["type"] == "mitigation"


class TestEuAiAct:
    def test_high_risk_for_law_enforcement(self):
        result = eu_ai_act.classify(
            "An LLM-based system to triage incoming security alerts at a federal agency."
        )
        assert result["tier"] == "high_risk"
        assert result["obligations"]
        assert result["annex_reference"]
        assert result["matched_triggers"]

    def test_prohibited_for_social_scoring(self):
        result = eu_ai_act.classify(
            "Social scoring of citizens by a municipal authority based on behavior."
        )
        assert result["tier"] == "prohibited"

    def test_limited_risk_for_chatbot(self):
        result = eu_ai_act.classify("A customer-service chatbot on a retail website.")
        assert result["tier"] == "limited_risk"

    def test_minimal_risk_fallback(self):
        result = eu_ai_act.classify("Spell-check feature in a word processor.")
        assert result["tier"] == "minimal_risk"

    def test_output_shape(self):
        result = eu_ai_act.classify("Generic AI feature.")
        expected = {
            "tier",
            "rationale",
            "obligations",
            "annex_reference",
            "tier_description",
            "matched_triggers",
        }
        assert expected <= set(result)


class TestEthics:
    @pytest.mark.parametrize("name", list(ethics.SUPPORTED))
    def test_each_framework_returns_scaffold(self, name: str):
        result = ethics.get(name)
        assert result["framework"] == name
        assert result["core_question"]
        assert isinstance(result["analytical_steps"], list) and result["analytical_steps"]
        assert isinstance(result["key_considerations"], list) and result["key_considerations"]

    def test_case_insensitive(self):
        result = ethics.get("Utilitarian")
        assert result["framework"] == "utilitarian"

    def test_unknown_framework_raises(self):
        with pytest.raises(ValueError):
            ethics.get("stoicism")


class TestMemo:
    def test_renders_all_sections(self):
        out = memo.format_memo(
            scenario="Deploy alert-triage LLM at a federal SOC.",
            pro_arguments=["Reduces mean time to triage.", "Frees analysts for hard cases."],
            con_arguments=["Prompt injection via alert payloads.", "Skill atrophy."],
            frameworks_cited=["NIST AI RMF MEASURE-2.7", "EU AI Act high-risk", "deontological"],
            recommendation="Pilot with human-in-the-loop and quarterly red-team.",
        )
        for header in (
            "# AI Governance Decision Memo",
            "## Scenario Summary",
            "## Analysis",
            "### Arguments For",
            "### Arguments Against",
            "## Frameworks Cited",
            "## Recommendation",
        ):
            assert header in out

    def test_handles_empty_lists(self):
        out = memo.format_memo(
            scenario="x",
            pro_arguments=[],
            con_arguments=[],
            frameworks_cited=[],
            recommendation="",
        )
        assert "_(none provided)_" in out
        assert "_(no recommendation provided)_" in out
