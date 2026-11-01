from backend.services.gesture_meanings import GestureMeaningService


def test_interpret_known_gesture():
    service = GestureMeaningService()
    result = service.interpret_gesture("thumbs_up")

    assert result["understood"] is True
    assert result["meaning"] == "agreement"
    assert "possible_meanings" in result


def test_generate_response_for_multiple_gestures():
    service = GestureMeaningService()
    result = service.generate_response(["wave", "thumbs_up"])

    assert result["understood"] is True
    assert len(result["gestures"]) == 2
    assert "response" in result
    assert [detail["gesture"] for detail in result["gesture_details"]] == [
        "wave",
        "thumbs_up",
    ]
    assert all(detail["suggested_response"] for detail in result["gesture_details"])


def test_gesture_details_include_a_specific_meaning_and_response_for_each_detected_hand():
    service = GestureMeaningService()
    result = service.generate_response(["wave", "wave"])

    assert len(result["gesture_details"]) == 2
    assert [detail["gesture"] for detail in result["gesture_details"]] == ["wave", "wave"]
    assert all(detail["meaning"] == "greeting" for detail in result["gesture_details"])
    assert all("Hello" in detail["suggested_response"] or "Hi" in detail["suggested_response"] or
               "Greetings" in detail["suggested_response"] for detail in result["gesture_details"])
    assert result["response"] == "I see you're communicating multiple things. Could you clarify what you need?"


def test_fist_response_explains_its_ambiguous_documented_meanings():
    service = GestureMeaningService()
    result = service.generate_response(["fist"])

    assert result["gesture_details"][0]["meaning"] == "power"
    assert "strength" in result["response"]
    assert "solidarity" in result["response"]
    assert "stop" in result["response"]
