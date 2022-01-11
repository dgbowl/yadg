"""

"""

def _process_header() -> dict:
    header = dict([l.split(",", 1) for l in header.split("\n")[1:-1]])
    comments
    pass

def _process_data(data) -> tuple[dict, dict]:
    data_lines = data.split("\n")[1:]
    columns = data_lines[0].split(",")
    assert columns == ["Angle", "Intensity"]
    angle, intensity = [list(z) for z in zip(*[l.split(",") for l in data_lines[1:-1]])]
    return angle, intensity


def process(fn, encoding="utf-8"):
    with open(fn, "r", encoding=encoding) as csv_file:
        csv = csv_file.read()
    # Split file into its sections.
    __, header, data = csv.split("[")
    # TODO:Assemble meta
    angle, intensity = _process_data(data)
    angle = {
        "n": angle,
        "s": None,  # TODO: from header scan step size
        "u": "2Theta (deg)",
    }
    intensity = {
        "n": intensity,
        "s": None,  # TODO:
        "u": "count",
    }
    # TODO: assemble datapoints
    data = (
        [
            {
                "fn": fn,
                "uts": None,  # TODO:
                "raw": trace,
            }
        ],
    )


if __name__ == "__main__":
    process(
        r"G:\Collaborators\Vetsch Nicolas\parsers\xrd\testing\210520step1_30min.csv"
    )
    print("")
