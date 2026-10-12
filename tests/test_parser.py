"""Dependency-free tests for observed panel zone payloads."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "custom_components" / "pgst_zone_manager" / "parser.py"
spec = importlib.util.spec_from_file_location("pgst_parser", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_observed_messages():
    samples = {
        "SOS from Remote\nZone:000": "000",
        "System Alarm\nZone:002Mudroom motion": "002",
        "Door/Window Open\nZone:010Kitchen": "010",
        "Door/Window Open\nZone:013": "013",
        "Panic Alarm\nZone:016": "016",
    }
    for message, expected in samples.items():
        assert module.parse_zone(message) == expected


def test_rejects_malformed_messages():
    for message in [None, "", "Zone:abc", "Zone:999", "Zone:0023", "No Zone"]:
        assert module.parse_zone(message) is None
