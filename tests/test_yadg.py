import pytest
import subprocess
import os
import json
from datatree import open_datatree

from .utils import pars_datagram_test, standard_datagram_test, compare_datatrees


def test_yadg_version():
    command = ["yadg", "--version"]
    subprocess.run(command, check=True)


def test_yadg_process_without_schema(datadir):
    command = ["yadg", "process"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_process_with_bad_schema(datadir):
    command = ["yadg", "process", "somefile.json"]
    with pytest.raises(AssertionError, match="Supplied schema file"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_process_with_one_positional_arg(datadir):
    os.chdir(datadir)
    command = ["yadg", "process", "test_schema.json"]
    subprocess.run(command, check=True)
    assert os.path.exists("datagram.nc")


def test_yadg_process_with_two_positional_args(datadir):
    os.chdir(datadir)
    command = ["yadg", "process", "test_schema.json", "test.datagram.nc"]
    subprocess.run(command, check=True)
    assert os.path.exists("test.datagram.nc")


def test_yadg_update_without_subcommand(datadir):
    os.chdir(datadir)
    command = ["yadg", "update"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_update_310(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "schema_3.1.0.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("schema_3.1.0.new.json")


def test_yadg_update_310_with_outfile(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "schema_3.1.0.json", "output.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("output.json")


def test_yadg_preset(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_preset_with_preset_folder(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("schema.json")


def test_yadg_preset_with_preset_folder_outfile(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "data_2.schema.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("data_2.schema.json")


def test_yadg_preset_with_preset_folder_p1(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "-p"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("datagram.nc")


def test_yadg_preset_with_preset_folder_p2(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "data_2.dg.nc", "-p"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("data_2.dg.nc")


def test_yadg_preset_with_preset_folder_p3(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "-p", "data_2.dg.nc"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("data_2.dg.nc")


def test_yadg_process_with_yml(datadir):
    os.chdir(datadir)
    command = ["yadg", "process", "test_schema.yml"]
    subprocess.run(command, check=True)
    assert os.path.exists("datagram.nc")


def test_yadg_preset_with_yml(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "-p", "data_2.preset.yaml", "data_2", "data_2.nc"]
    subprocess.run(command, check=True)
    assert os.path.exists("data_2.nc")


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
def test_yadg_preset_archive(packwith, suffix, datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "-pa", "data_2.preset.yaml", "data_2", "dg.nc"]
    if packwith is not None:
        command.append("--packwith")
        command.append(packwith)
    subprocess.run(command, check=True)
    assert os.path.exists("dg.nc")
    assert os.path.exists(f"dg.{suffix}")


def test_yadg_preset_roundtrip_uts(datadir):
    ts = {"nsteps": 1, "step": 0, "nrows": 20, "point": 19}
    ts["pars"] = {"uts": {"value": 1652254017.1712718}}
    os.chdir(datadir)
    command = ["yadg", "preset", "-p", "data_4.preset.json", "data_4", "data_4.nc"]
    subprocess.run(command, check=True)
    assert os.path.exists("data_4.nc")
    dg = open_datatree("data_4.nc")
    standard_datagram_test(dg, ts)
    pars_datagram_test(dg, ts)


@pytest.mark.parametrize(
    "filetype, infile",
    [
        ("eclab.mpr", "cp.mpr"),
        ("marda:biologic-mpr", "cp.mpr"),
        ("biologic-mpr", "cp.mpr"),
    ],
)
def test_yadg_extract(filetype, infile, datadir):
    os.chdir(datadir)
    command = ["yadg", "extract", filetype, infile, "test.nc"]
    subprocess.run(command, check=True)
    assert os.path.exists("test.nc")
    ret = open_datatree("test.nc")
    ref = open_datatree(f"ref.{infile}.nc")
    compare_datatrees(ret, ref)


@pytest.mark.parametrize(
    "filetype, infile, flag",
    [
        ("eclab.mpr", "cp.mpr", "-m"),
        ("marda:biologic-mpr", "cp.mpr", "--meta-only"),
        ("biologic-mpr", "cp.mpr", "-m"),
    ],
)
def test_yadg_extract_meta_only(filetype, infile, flag, datadir):
    os.chdir(datadir)
    command = ["yadg", "extract", filetype, infile, flag]
    subprocess.run(command, check=True)
    assert os.path.exists("cp.json")
    with open("cp.json", "r") as inp:
        ret = json.load(inp)
    for key in {"attrs", "coords", "dims", "data_vars"}:
        assert key in ret.keys()


def test_yadg_preset_dataschema_compat(datadir):
    os.chdir(datadir)
    sfns = [fn for fn in os.listdir() if fn.endswith("yml") and fn.startswith("ds")]
    ncs = []
    for fn in sfns:
        command = ["yadg", "preset", "-p", fn, "ds_compat", fn.replace("yml", "nc")]
        subprocess.run(command, check=True)
        ncs.append((fn, open_datatree(fn.replace("yml", "nc"))))
    refname, ref = ncs[0]
    for tup in ncs[1:]:
        retname, ret = tup
        print(f"comparing {refname} with {retname}")
        compare_datatrees(ret, ref)
