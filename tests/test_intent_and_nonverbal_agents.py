from backend.agents.intent_agent import IntentAgent
from backend.agents.nonverbal_agent import NonVerbalAgent


def test_intent_agent_fallback_detects_question():
    agent = IntentAgent()
    result = agent._fallback_intent("What is this?")

    assert result["intent"] == "ask_question"
    assert result["confidence"] >= 0.7


def test_nonverbal_agent_fallback_preserves_input_and_tokens():
    agent = NonVerbalAgent()
    result = agent._fallback_interpretation("Hi 👋", [{"token": "👋", "meaning": "greeting"}])

    assert result["original_input"] == "Hi 👋"
    assert "semantic_meaning" in result
    assert result["interpretation_method"] == "rule_based"
