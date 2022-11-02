import argparse

import pytest

from aaargs import Argument, ArgumentParser


def test_subinit_kwargs():
    class Parser(ArgumentParser, description="Lorem Ipsum"):
        pass

    assert Parser.description == "Lorem Ipsum"

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"

    assert Parser.description == "Lorem Ipsum"

    with pytest.raises(AttributeError):

        class Parser(ArgumentParser, wrong_kwarg="Lorem Ipsum"):
            pass


def test_get_parser():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"

        filename = Argument()

    parser = Parser.get_parser()
    assert parser.description == "Lorem Ipsum"
    assert isinstance(parser, argparse.ArgumentParser)


def test_parse_args():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument()

    args = Parser.parse_args(["myfile"])
    assert args.filename == "myfile"

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument()
        encoding = Argument("-e", "--encoding")

    args = Parser.parse_args(["myfile", "-e", "utf-8"])
    assert args.filename == "myfile"
    assert args.encoding == "utf-8"

    args = Parser.parse_args(["myfile", "--encoding", "utf-8"])
    assert args.filename == "myfile"
    assert args.encoding == "utf-8"

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument()
        e = Argument("-e")

    args = Parser.parse_args(["myfile", "-e", "utf-8"])
    assert args.filename == "myfile"
    assert args.e == "utf-8"


def test_parse_args_with_defaults():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument("--filename", default="myfile.txt", required=False)

    args = Parser.parse_args("")
    assert args.filename == "myfile.txt"


def test_args_positional():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument(positional=True)

    args = Parser.parse_args(["myfile"])
    assert args.filename == "myfile"

    with pytest.raises(SystemExit):
        _ = Parser.parse_args(["--filename", "myfile"])

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument(positional=False)

    args = Parser.parse_args(["--filename", "myfile"])
    assert args.filename == "myfile"

    with pytest.raises(SystemExit):
        _ = Parser.parse_args(["myfile"])


def test_args_wrong_name():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument("--encoding")

    with pytest.raises(AttributeError):
        _ = Parser.parse_args(["--encoding", "utf-8"])

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        encoding = Argument("-e")

    with pytest.raises(AttributeError):
        _ = Parser.parse_args(["-e", "utf-8"])


def test_create_instance():
    class Parser(ArgumentParser):
        filename = Argument()
        encoding = Argument(positional=False, default="utf-8")

    with pytest.raises(TypeError):
        _ = Parser()
    parser = Parser(filename="my_file")
    assert parser.filename == "my_file"
    assert parser.encoding == "utf-8"
