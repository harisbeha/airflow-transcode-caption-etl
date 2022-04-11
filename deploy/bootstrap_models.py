
# Collect Static Files
# Note: Ensure that the correct target bucket is set and that permissions are available

# Create Social Auth Apps

# Create System Users

# Create Preset templates
# TODO Add Rush 12
# Default prefixes
# TX_
# TRANS_
# FOREIGN_
# AD_
presets = [
    {
        "title": "TX_STD",
        "job_type": "TX",
        "rush_24": False,
        "true_verbatim": False,
        "speaker_id": False,
        "source_languages": [],
        "target_languages": [],
        "is_default": True,
    },
    {
        "title": "TX_RUSH_24",
        "job_type": "TX",
        "rush_24": True,
        "true_verbatim": False,
        "speaker_id": False,
        "source_languages": [],
        "target_languages": [],
        "is_default": True,
    }, 
    {
        "title": "TRANSL_SP_STD",
        "job_type": "TRANSL",
        "rush_24": False,
        "true_verbatim": False,
        "speaker_id": False,
        "source_languages": ["en"],
        "target_languages": ["es"],
        "is_default": True,
    },
    {
        "title": "TRANSL_FR_STD",
        "job_type": "TRANSL",
        "rush_24": False,
        "true_verbatim": False,
        "speaker_id": False,
        "source_languages": ["en"],
        "target_languages": ["fr"],
        "is_default": True,
    },
    {
        "title": "TX_STD_SPEAKER_ID",
        "job_type": "TX",
        "rush_24": False,
        "true_verbatim": False,
        "speaker_id": True,
        "source_languages": [],
        "target_languages": [],
        "is_default": True,
        }, 
    {
        "title": "TX_MECH",
        "job_type": "TX",
        "rush_24": False,
        "true_verbatim": False,
        "speaker_id": False,
        "source_languages": [],
        "target_languages": [],
        "is_default": True,
    }
]