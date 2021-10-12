datagram_step = {
    "type": dict,
    "all": {
        "metadata": {
            "type": dict,
            "all": {
                "tag": {"type": str}
            },
            "allow": True
        },
        "timesteps": {
            "type": list,
            "each": {
                "type": dict,
                "all": {"uts": {"type": float}},
                "any": {
                    "fn": {"type": str},
                    "raw": {"type": dict},
                    "derived": {"type": dict}
                }
            }
        }
    },
    "any": {
        "common": {"type": dict}
    }
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
                "datagram_version": {"type": str}
            }
        },
        "data": {
            "type": list,
            "each": datagram_step
        }
    }
}
