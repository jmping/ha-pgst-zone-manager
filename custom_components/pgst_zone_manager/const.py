"""Constants and initial zone assignments."""
DOMAIN = "pgst_zone_manager"
CONF_SOURCE = "source_entity"
CONF_ZONES = "zones"
MODE_MOTION = "motion"
MODE_ACTIVITY = "contact_activity"
MODE_TOGGLE = "toggle_contact"
MODE_BUTTON = "button"
MODE_DISABLED = "disabled"
MODES = [MODE_MOTION, MODE_ACTIVITY, MODE_TOGGLE, MODE_BUTTON, MODE_DISABLED]
DEFAULT_ZONES = {
    "000": {"name": "Remote SOS", "mode": MODE_BUTTON},
    "001": {"name": "Entry Motion", "mode": MODE_MOTION, "timeout": 120},
    "002": {"name": "Mudroom Motion", "mode": MODE_MOTION, "timeout": 120},
    "003": {"name": "Hall Motion", "mode": MODE_MOTION, "timeout": 120},
    "004": {"name": "Motion 004", "mode": MODE_MOTION, "timeout": 120},
    "005": {"name": "Motion 005", "mode": MODE_MOTION, "timeout": 120},
    "006": {"name": "Contact 006 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "007": {"name": "Contact 007 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "008": {"name": "Main Bathroom Window", "mode": MODE_TOGGLE, "device_class": "window", "enabled": False},
    "009": {"name": "Office Window", "mode": MODE_TOGGLE, "device_class": "window", "enabled": False},
    "010": {"name": "Kitchen Window", "mode": MODE_TOGGLE, "device_class": "window", "enabled": False},
    "011": {"name": "Contact 011 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "012": {"name": "Main Bedroom Window", "mode": MODE_TOGGLE, "device_class": "window", "enabled": False},
    "013": {"name": "Contact 013 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "014": {"name": "Contact 014 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "015": {"name": "Contact 015 Activity", "mode": MODE_ACTIVITY, "timeout": 10},
    "016": {"name": "Panic Button", "mode": MODE_BUTTON},
}
