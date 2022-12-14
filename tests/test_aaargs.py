import argparse

import pytest

import aaargs
from aaargs import Argument, ArgumentParser


def test_version():
    assert aaargs.__version__ == "0.1.3"


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
        filename = Argument(positional=True)

    args = Parser.parse_args(["myfile"])
    assert args.filename == "myfile"
    assert Parser(filename="myfile").filename == "myfile"

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument(positional=True)
        encoding = Argument("-e", "--encoding")

    args = Parser.parse_args(["myfile", "-e", "utf-8"])
    assert args.filename == "myfile"
    assert args.encoding == "utf-8"
    args = Parser(filename="myfile", encoding="utf-8")
    assert args.filename == "myfile"
    assert args.encoding == "utf-8"

    args = Parser.parse_args(["myfile", "--encoding", "utf-8"])
    assert args.filename == "myfile"
    assert args.encoding == "utf-8"

    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument(positional=True)
        e = Argument("-e")

    args = Parser.parse_args(["myfile", "-e", "utf-8"])
    assert args.filename == "myfile"
    assert args.e == "utf-8"
    args = Parser(filename="myfile", e="utf-8")
    assert args.filename == "myfile"
    assert args.e == "utf-8"


def test_parse_args_with_defaults():
    class Parser(ArgumentParser):
        description = "Lorem Ipsum"
        filename = Argument("--filename", default="myfile.txt", required=False)

    args = Parser.parse_args("")
    assert args.filename == "myfile.txt"

    assert Parser().filename == "myfile.txt"


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

    parser = Parser()
    assert parser.filename is None

    parser = Parser(filename="my_file")
    assert parser.filename == "my_file"
    assert parser.encoding == "utf-8"


@pytest.mark.parametrize("annotation", (bool, "bool"))  # test future implementation.
def test_store_true(annotation):
    class Parser(ArgumentParser):
        name: str = Argument(positional=True)
        verbose: annotation = Argument()

    parser = Parser.parse_args(["someone", "--verbose"])
    assert parser.verbose
    assert parser.name == "someone"

    parser = Parser.parse_args(["someone"])
    assert not parser.verbose
    assert parser.name == "someone"

    with pytest.raises(TypeError):

        class Parser(ArgumentParser):
            name: str = Argument()
            verbose: annotation = Argument(positional=True)  # must not be positional

    with pytest.raises(AttributeError):

        class Parser(ArgumentParser):
            name: str = Argument(positional=True)
            verbose: annotation = Argument("--verb")

        Parser.parse_args(["someone"])

    class Parser(ArgumentParser):
        name: str = Argument(positional=True)
        verbose: annotation = Argument("--verbose")

    parser = Parser.parse_args(["someone", "--verbose"])
    assert parser.verbose is True
    assert parser.name == "someone"

    parser = Parser.parse_args(["someone"])
    assert parser.verbose is False
    assert parser.name == "someone"

    assert Parser().verbose is False
    assert Parser(verbose=True).verbose is True

    class Parser(ArgumentParser):
        name: str = Argument(positional=True)
        verbose: annotation = Argument(default=True)

    parser = Parser.parse_args(["someone"])
    assert parser.verbose
    assert parser.name == "someone"


def test_wrong_annotations():
    with pytest.raises(ValueError):

        class Parser(ArgumentParser):
            name: bool = Argument(default="someone")


def test_required():
    with pytest.raises(TypeError):
        # required is invalid for positionals
        class Parser(ArgumentParser):
            name: str = Argument(positional=True, required=True)

    class Parser(ArgumentParser):
        name: str = Argument(required=False, default=None)

    parser = Parser()
    assert parser.name is None

    class Parser(ArgumentParser):
        name: str = Argument(required=False)

    parser = Parser()
    assert parser.name is None

    class Parser(ArgumentParser):
        name: str = Argument(required=True)

    with pytest.raises(TypeError):
        _ = Parser()
