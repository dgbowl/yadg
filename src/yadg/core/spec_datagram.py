from importlib import metadata as ilmd

datagram_version = ilmd.version("yadg")

datagram_step = {
    "type": dict,
    "all": {
        "metadata": {
            "type": dict,
            "all": {
                "tag": {"type": str},
                "parser": {"type": str},
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
