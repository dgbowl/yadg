datagram_version = "4.0.rc1"

datagram_step = {
    "type": dict,
    "all": {
        "metadata": {
            "type": dict,
            "all": {
                "tag": {"type": str},
                "parser": {
                    "type": dict,
                    "each": {
                        "type": dict,
                        "all": {"version": {"type": str}},
                        "allow": True,
                    },
                },
            },
            "allow": True,
        },
        "data": {
            "type": list,
            "each": {
                "type": dict,
                "all": {"uts": {"type": float}},
                "any": {
                    "fn": {"type": str},
                    "raw": {"type": dict},
                    "derived": {"type": dict},
                },
            },
        },
    },
    "any": {"common": {"type": dict}},
}

datagram = {
    "type": dict,
    "all": {
        "metadata": {
            "type": dict,
            "all": {
                "provenance": {"type": dict},
                "date": {"type": str},
                "input_schema": {"type": dict},
                "datagram_version": {"type": str},
            },
        },
        "steps": {"type": list, "each": datagram_step},
    },
}
