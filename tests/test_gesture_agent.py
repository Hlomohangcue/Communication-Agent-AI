from backend.agents.gesture_agent import GestureAgent


def test_text_to_gesture_phrase_match():
    agent = GestureAgent()
    result = agent.text_to_gestures("good morning")

    assert result["method"] == "phrase_match"
    assert "gesture_sequence" in result


def test_text_to_gesture_keyword_match():
    agent = GestureAgent()
    result = agent.text_to_gestures("I need water")

    assert result["method"] in {"keyword_match", "ai_translation", "fallback"}
    assert "gesture_sequence" in result
