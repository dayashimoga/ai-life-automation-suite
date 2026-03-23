import pytest
from services.captioning import CaptioningService

service = CaptioningService()

def test_extract_date_secondary_pattern():
    # Test DDMMYYYY pattern
    date = service._extract_date_from_name("photo_15_03_2024.jpg")
    assert date == "2024-03-15"

def test_reverse_geocode_regions():
    assert service._reverse_geocode(40, -100) == "United States"
    assert service._reverse_geocode(50, 10) == "Europe"
    assert service._reverse_geocode(20, 80) == "India"
    assert service._reverse_geocode(-30, 130) == "Australia"
    assert "Coordinates" in service._reverse_geocode(0, 0)

def test_generate_caption_types():
    # Video with scene (scene takes precedence)
    assert "travel" in service.generate_caption("vacation.mp4").lower()
    # Video without scene
    assert "video memory" in service.generate_caption("movie.mp4").lower()
    # Screenshot
    assert "screenshot" in service.generate_caption("screenshot_2024.png").lower()
    # Camera prefix
    assert "captured moment" in service.generate_caption("IMG_001.jpg")
    # Personal memory (fallback)
    assert "personal memory" in service.generate_caption("random_file.txt")

def test_extract_tags_video():
    tags = service.extract_tags("trip.mp4")
    assert "video" in tags
    assert "travel" in tags

def test_guess_location_hints():
    assert service.guess_location("trip_to_paris.jpg") == "Paris, France"
    assert service.guess_location("vacation_in_tokyo.png") == "Tokyo, Japan"
    assert service.guess_location("random.jpg") == "Location pending EXIF analysis"

def test_parse_exif_gps_invalid():
    # Should handle non-existent file or non-JPEG gracefully
    assert service._parse_exif_gps("nonexistent.jpg") is None
