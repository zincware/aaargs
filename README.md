[![coveralls](https://coveralls.io/repos/github/zincware/aaargs/badge.svg)](https://coveralls.io/github/zincware/aaargs)
![PyTest](https://github.com/zincware/aaargs/actions/workflows/pytest.yaml/badge.svg)
[![PyPI version](https://badge.fury.io/py/aaargs.svg)](https://badge.fury.io/py/aaargs)

# Aaargs ...

I'm not a huge fan of the [argparse](https://docs.python.org/3/library/argparse.html) library that ships with Python.
Personally, I much prefer  [typer](https://typer.tiangolo.com/) or [click](https://click.palletsprojects.com/).
But `argparse` is often used so this is my approach in bringing at least autocompletion to the argparse library.

Let us take a look at the official documentation and use their examples:

```python
import argparse

parser = argparse.ArgumentParser(
                    prog = 'ProgramName',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')

parser.add_argument('filename')           # positional argument
parser.add_argument('-c', '--count')      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

args = parser.parse_args()
print(args.filename, args.count, args.verbose)
```

Why isn't the `argparse.ArgumentParser` a container class, like a dataclass?

So my approach to *solve* this looks like this:

```python
from aaargs import ArgumentParser, Argument

class MyParser(ArgumentParser):
    rog = "ProgramName"
    description = "What the program does"
    epilog = "Text at the bottom of help"

    # You can define arguments directly
    filename = Argument()  # positional argument
    encoding = Argument(positional=False)  # keyword argument '--encoding'
    
    # or pass the 'name_or_flags' argument
    count = Argument("-c", "--count")
    verbose = Argument("-v", "--verbose", action="store_true")

parser: argparse.ArgumentParser = MyParser.get_parser()
args: MyParser = MyParser.parse_args()
```

You can also print the parser just like the original:
```python
args = MyParser.parse_args(
        ["README.md", "--encoding", "utf-8", "-c", "3"]
    )

print(args)
>>> MyParser(count='3', encoding='utf-8', filename='README.md', verbose=False)
```

You can also create a Parser using keyword arguments if you prefer (I don't):

```python
from aaargs import ArgumentParser

class MyParser(
    ArgumentParser,
    prog="ProgramName",
    description="What the program does",
    epilog="Text at the bottom of help",
):
    ...
```