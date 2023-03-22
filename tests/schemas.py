ts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "suffix": "wrong"}}],
}
ts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"files": ["ts1.dummy.json"]}}],
}
ts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {"folders": ["."], "contains": ".dummy."}}],
}
ts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["ts0.dummy.json", "ts1.dummy.json"]},
        }
    ],
}
ts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"folders": ["."], "prefix": "ts", "contains": "1"},
        }
    ],
}
fts0 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parse": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts1 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dumm",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts2 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {
                "files": ["dummy_schema_1.json", "dummy_schema_2.json"],
                "folders": ["."],
            },
        }
    ],
}
fts3 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [{"parser": "dummy", "import": {}}],
}
fts4 = {
    "metadata": {"provenance": "manual", "schema_version": "4.0.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "key": "value",
        }
    ],
}

ts5 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {
                "folders": ["."],
                "suffix": "json",
                "contains": "schema",
                "exclude": "3.1.0",
            },
            "parameters": {},
        }
    ],
}

fts5 = {
    "metadata": {"provenance": "wrong", "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts6 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.0"},
    "steps": [
        {
            "parser": "dummy",
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts7 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "parser": "dummy",
            "import": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
        }
    ],
}
fts8 = {
    "metadata": {"provenance": {"type": "manual"}, "version": "4.1"},
    "steps": [
        {
            "input": {"files": ["dummy_schema_1.json", "dummy_schema_2.json"]},
            "parameters": {"k": "v"},
        }
    ],
}
