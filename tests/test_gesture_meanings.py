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
