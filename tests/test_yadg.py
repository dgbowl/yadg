import json
import shutil
import subprocess

import numpy as np
import pytest
from xarray import open_datatree

from yadg.dgutils.schemautils import __latest_dataschema__

from .utils import compare_datatrees


def test_yadg_version():
    command = ["yadg", "--version"]
    subprocess.run(command, check=True)


def test_yadg_process_without_schema(tmp_path):
    command = ["yadg", "process"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_process_with_bad_schema(tmp_path):
    command = ["yadg", "process", "somefile.json"]
    with pytest.raises(AssertionError, match="Supplied dataschema filename"):
        try:
            subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_process_with_one_positional_arg(datadir, tmp_path):
    # By default outputs to working directory, so copy to temp location
    for file in ("test_schema.json", "data_3.1.0/00-experiment/measurement.csv"):
        (tmp_path / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(datadir / file,tmp_path / file)
    command = ["yadg", "process", "test_schema.json"]
    subprocess.run(command, check=True, cwd=tmp_path)
    assert (tmp_path / "datagram.nc").exists()


def test_yadg_process_with_two_positional_args(datadir, tmp_path):
    outfile = tmp_path / "test.datagram.nc"
    command = ["yadg", "process", "test_schema.json", str(outfile)]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()


def test_yadg_update_without_subcommand(tmp_path):
    command = ["yadg", "update"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_update_310_with_outfile(datadir, tmp_path):
    outfile = tmp_path / "output.json"
    command = ["yadg", "update", "schema_3.1.0.json", str(outfile)]
    subprocess.run(command, check=True, capture_output=True, cwd=datadir)
    assert outfile.exists()

    with open(outfile, "r") as inp:
        ret = json.load(inp)
    assert ret["version"] == __latest_dataschema__


def test_yadg_preset(tmp_path):
    command = ["yadg", "preset"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_preset_with_preset_folder(datadir, tmp_path):
    command = [
        "yadg",
        "preset",
        str(datadir / "data_2.preset.json"),
        str(datadir / "data_2"),
    ]
    subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
    assert (tmp_path / "schema.json").exists()


def test_yadg_preset_with_preset_folder_outfile(datadir, tmp_path):
    outfile = tmp_path / "data_2.schema.json"
    command = ["yadg", "preset", "data_2.preset.json", "data_2", str(outfile)]
    subprocess.run(command, check=True, capture_output=True, cwd=datadir)
    assert outfile.exists()


def test_yadg_preset_with_preset_folder_p1(datadir, tmp_path):
    command = [
        "yadg",
        "preset",
        str(datadir / "data_2.preset.json"),
        str(datadir / "data_2"),
        "-p",
    ]
    subprocess.run(command, check=True, capture_output=True, cwd=tmp_path)
    assert (tmp_path / "datagram.nc").exists()


def test_yadg_preset_with_preset_folder_p2(datadir, tmp_path):
    outfile = tmp_path / "data_2.dg.nc"
    command = ["yadg", "preset", "data_2.preset.json", "data_2", str(outfile), "-p"]
    subprocess.run(command, check=True, capture_output=True, cwd=datadir)
    assert outfile.exists()


def test_yadg_preset_with_preset_folder_p3(datadir, tmp_path):
    outfile = tmp_path / "data_2.dg.nc"
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "-p", str(outfile)]
    subprocess.run(command, check=True, capture_output=True, cwd=datadir)
    assert outfile.exists()


def test_yadg_process_with_metadata(datadir, tmp_path):
    outfile = tmp_path / "datagram.nc"
    command = ["yadg", "process", "test_schema.yml", str(outfile)]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    ret = open_datatree(outfile, engine="h5netcdf")
    ref = open_datatree(datadir / "datagram.nc.ref", engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)


def test_yadg_preset_with_metadata(datadir, tmp_path):
    outfile = tmp_path / "data_2.nc"
    command = ["yadg", "preset", "-p", "data_2.preset.yaml", "data_2", str(outfile)]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    ret = open_datatree(outfile, engine="h5netcdf")
    ref = open_datatree(datadir / "data_2.nc.ref", engine="h5netcdf")
    print(f"{ret.attrs=}")
    print(f"{ref.attrs=}")
    compare_datatrees(ret, ref, thislevel=True, descend=True)


@pytest.mark.parametrize(
    "packwith, suffix",
    [
        (None, "zip"),
        ("zip", "zip"),
        ("tar", "tar"),
        ("gztar", "tar.gz"),
        ("xztar", "tar.xz"),
        ("bztar", "tar.bz2"),
    ],
)
def test_yadg_preset_archive(packwith, suffix, datadir, tmp_path):
    outfile = tmp_path / "dg.nc"
    command = ["yadg", "preset", "-pa", "data_2.preset.yaml", "data_2", str(outfile)]
    if packwith is not None:
        command.append("--packwith")
        command.append(packwith)
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    assert (tmp_path / f"dg.{suffix}").exists()


def test_yadg_preset_roundtrip_uts(datadir, tmp_path):
    ts = {"nsteps": 1, "step": 0, "nrows": 20, "point": 19}
    ts["pars"] = {"uts": {"value": 1652254017.1712718}}
    outfile = tmp_path / "data_4.nc"
    command = ["yadg", "preset", "-p", "data_4.preset.json", "data_4", str(outfile)]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    ret = open_datatree(outfile, engine="h5netcdf")
    print(f"{ret=}")
    assert ret["worker"]["uts"].shape == (20,)
    np.testing.assert_almost_equal(ret["worker"]["uts"][-1], 1652254017.1712718)


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("eclab.mpr", "cp.mpr"),
        ("agilent.ch", "agilent.CH"),
        ("fusion.json", "fusion.fusion-data"),
        ("yadg.json", "ds.4.2.dg.json"),
    ],
)
def test_yadg_extract_with_metadata(filetype, infile, datadir, tmp_path):
    outfile = tmp_path / "test.nc"
    command = [
        "yadg",
        "extract",
        filetype,
        infile,
        str(outfile),
        "--locale",
        "en_GB",
        "--timezone",
        "Europe/Berlin",
    ]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    ret = open_datatree(outfile, engine="h5netcdf")
    ref = open_datatree(datadir / f"{infile}.nc", engine="h5netcdf")
    # let's delete metadata we know will be wrong
    compare_datatrees(ret, ref, thislevel=True, descend=True)


@pytest.mark.parametrize(
    "filetype, infile, flag",
    [
        ("eclab.mpr", "cp.mpr", "--meta-only"),
        ("agilent.ch", "agilent.CH", "-m"),
        ("fusion.json", "fusion.fusion-data", "--meta-only"),
    ],
)
def test_yadg_extract_meta_only(filetype, infile, flag, datadir, tmp_path):
    # By default outputs to working directory, so copy to temp location
    (tmp_path / infile).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(datadir / infile, tmp_path / infile)
    command = [
        "yadg",
        "extract",
        filetype,
        infile,
        flag,
        "--locale",
        "en_GB",
        "--timezone",
        "Europe/Berlin",
    ]
    subprocess.run(command, check=True, cwd=tmp_path)
    outfile = tmp_path / (infile.split(".")[0] + ".json")
    assert outfile.exists()
    with open(outfile, "r") as inp:
        ret = json.load(inp)
    print(f"{ret=}")
    for node in ret.values():
        for key in {"attrs", "coords", "dims", "data_vars"}:
            assert key in node.keys()


def test_yadg_preset_dataschema_compat(datadir, tmp_path):
    sfns = [f.name for f in datadir.glob("ds*.yml")]
    ncs = []
    for fn in sfns:
        outfile = tmp_path / fn.replace("yml", "nc")
        command = ["yadg", "preset", "-p", fn, "ds_compat", str(outfile)]
        subprocess.run(command, check=True, cwd=datadir)
        ncs.append((fn, open_datatree(outfile, engine="h5netcdf")))
    _, ref = ncs[0]
    for name, ret in ncs[1:]:
        try:
            compare_datatrees(ret, ref)
        except AssertionError as e:
            e.args = (e.args[0] + f"\nFailed on file {name!r}.\n",)
            raise e


@pytest.mark.parametrize(
    "filetype, infile, locale",
    [
        ("eclab.mpt", "mb.issue_95.de.mpt", "de_DE"),
    ],
)
def test_yadg_extract_locale_metadata(filetype, infile, locale, datadir, tmp_path):
    outfile = tmp_path / "test.nc"
    command = [
        "yadg",
        "extract",
        "--locale",
        locale,
        filetype,
        infile,
        str(outfile),
        "--timezone",
        "Europe/Berlin",
    ]
    subprocess.run(command, check=True, cwd=datadir)
    assert outfile.exists()
    ret = open_datatree(outfile, engine="h5netcdf")
    ref = open_datatree(datadir / f"{infile}.nc", engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)


@pytest.mark.parametrize(
    "filetype, infile, suffix",
    [
        ("ezchrom.asc", "ezchrom-asc.zip", None),
        ("ezchrom.asc", "ezchrom-txt.zip", ".txt"),
        ("fusion.zip", "fusion-json.zip", None),
    ],
)
def test_yadg_extract_from_zip(filetype, infile, suffix, datadir, tmp_path):
    outfile = tmp_path / "test.nc"
    command = [
        "yadg",
        "extract",
        filetype,
        infile,
        str(outfile),
        "--locale",
        "en_GB",
        "--timezone",
        "Europe/Berlin",
    ]
    if suffix is not None:
        command.append("--suffix")
        command.append(suffix)
    subprocess.run(command, check=True, cwd=datadir)
    ret = open_datatree(outfile, engine="h5netcdf")
    ref = open_datatree(datadir / f"{infile}.nc", engine="h5netcdf")
    compare_datatrees(ret, ref, thislevel=True, descend=True)
