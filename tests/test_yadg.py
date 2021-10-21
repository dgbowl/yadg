import pytest
import subprocess
import os

from utils import datadir

def test_yadg_version():
    command = ["yadg", "--version"]
    subprocess.run(command, check = True)

def test_yadg_without_schema():
    command = ["yadg"]
    with pytest.raises(subprocess.CalledProcessError, match = "exit status 2"):
        subprocess.run(command, check = True)

def test_yadg_with_bad_schema():
    command = ["yadg", "--schemafile", "somefile.json"]
    with pytest.raises(subprocess.CalledProcessError, match = "exit status 2"):
        subprocess.run(command, check = True)

def test_yadg_with_schema(datadir):
    os.chdir(datadir)
    command = ["yadg", "--schemafile", "test_schema.json"]
    subprocess.run(command, check = True)
    assert os.path.exists("datagram.json")

def test_yadg_with_schema_and_dump(datadir):
    os.chdir(datadir)
    command = ["yadg", "--schemafile", "test_schema.json", "--dump", "dg.json"]
    subprocess.run(command, check = True)
    assert os.path.exists("dg.json")

def test_yadg_with_one_positional_arg(datadir):
    os.chdir(datadir)
    command = ["yadg", "test_schema.json"]
    subprocess.run(command, check = True)
    assert os.path.exists("datagram.json")

def test_yadg_with_two_positional_args(datadir):
    os.chdir(datadir)
    command = ["yadg", "test_schema.json", "test.datagram.json"]
    subprocess.run(command, check = True)
    assert os.path.exists("test.datagram.json")

def test_yadg_with_positional_schema_and_dump(datadir):
    os.chdir(datadir)
    command = ["yadg", "--dump", "test.datagram.json", "test_schema.json"]
    subprocess.run(command, check = True)
    assert os.path.exists("test.datagram.json")