import pytest
import subprocess
import os
import json

from .utils import pars_datagram_test, standard_datagram_test


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
    assert os.path.exists("datagram.json")


def test_yadg_process_with_two_positional_args(datadir):
    os.chdir(datadir)
    command = ["yadg", "process", "test_schema.json", "test.datagram.json"]
    subprocess.run(command, check=True)
    assert os.path.exists("test.datagram.json")


def test_yadg_update_without_subcommand(datadir):
    os.chdir(datadir)
    command = ["yadg", "update"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_update_schema_without_arg(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "schema"]
    with pytest.raises(AssertionError, match="error: the following arguments"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_update_schema_310(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "schema", "schema_3.1.0.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("schema_3.1.0.new.json")


def test_yadg_update_schema_310_with_outfile(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "schema", "schema_3.1.0.json", "output.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("output.json")


def test_yadg_update_datagram_310(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "datagram", "datagram_3.1.0.json"]
    with pytest.raises(AssertionError, match="Updating datagrams older than version"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


def test_yadg_update_datagram_310_with_outfile(datadir):
    os.chdir(datadir)
    command = ["yadg", "update", "datagram", "datagram_3.1.0.json", "output.json"]
    with pytest.raises(AssertionError, match="Updating datagrams older than version"):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            assert False, err.stderr


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
    assert os.path.exists("datagram.json")


def test_yadg_preset_with_preset_folder_p2(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "data_2.dg.json", "-p"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("data_2.dg.json")


def test_yadg_preset_with_preset_folder_p3(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "data_2.preset.json", "data_2", "-p", "data_2.dg.json"]
    subprocess.run(command, check=True, capture_output=True)
    assert os.path.exists("data_2.dg.json")


def test_yadg_process_with_yml(datadir):
    os.chdir(datadir)
    command = ["yadg", "process", "test_schema.yml"]
    subprocess.run(command, check=True)
    assert os.path.exists("datagram.json")


def test_yadg_preset_with_yml(datadir):
    os.chdir(datadir)
    command = ["yadg", "preset", "-p", "data_2.preset.yaml", "data_2", "data_2.dg.json"]
    subprocess.run(command, check=True)
    assert os.path.exists("data_2.dg.json")


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
    command = ["yadg", "preset", "-pa", "data_2.preset.yaml", "data_2", "dg.json"]
    if packwith is not None:
        command.append("--packwith")
        command.append(packwith)
    subprocess.run(command, check=True)
    assert os.path.exists("dg.json")
    assert os.path.exists(f"dg.{suffix}")


def test_yadg_preset_externaldate(datadir):
    ts = {"nsteps": 1, "step": 0, "nrows": 20, "point": 19}
    ts["pars"] = {"uts": {"value": 1652254017.1712718}}
    os.chdir(datadir)
    command = ["yadg", "preset", "-p", "data_4.preset.json", "data_4", "data_4.dg.json"]
    subprocess.run(command, check=True)
    assert os.path.exists("data_4.dg.json")
    with open("data_4.dg.json", "r") as inf:
        dg = json.load(inf)
    standard_datagram_test(dg, ts)
    pars_datagram_test(dg, ts)
